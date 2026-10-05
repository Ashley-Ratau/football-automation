const http = require("http");
const fs = require("fs");
const fsp = require("fs/promises");
const path = require("path");
const { spawn } = require("child_process");

const PORT = Number(process.env.PORT || 4173);
const APP_ROOT = __dirname;
const WORKSPACE_ROOT = path.resolve(APP_ROOT, "..");
const PUBLIC_ROOT = path.join(APP_ROOT, "public");

const DOCS = [
  ["01 idea brief.md", "Idea Brief"],
  ["02 research dossier.md", "Research Dossier"],
  ["03 script.md", "Script"],
  ["04 clip map.csv", "Clip Map"],
  ["05 clip sourcing plan.md", "Clip Sourcing Plan"],
  ["06 asset acquisition log.md", "Asset Log"],
  ["07 edit brief.md", "Edit Brief"],
  ["08 voiceover log.md", "Voiceover Log"],
];

const STAGES = [
  { id: "idea", label: "Idea", files: ["01 idea brief.md"] },
  { id: "research", label: "Research", files: ["02 research dossier.md"] },
  { id: "script", label: "Script", files: ["03 script.md"] },
  { id: "clips", label: "Clip Map", files: ["04 clip map.csv", "05 clip sourcing plan.md"] },
  { id: "voiceover", label: "Voiceover", folders: ["assets/voiceover"] },
  { id: "assets", label: "Assets", folders: ["assets/editor_package", "assets/selected"] },
  { id: "capcut", label: "CapCut", folders: ["CapCut Workflow"] },
  { id: "upload", label: "Upload", files: ["CapCut Workflow/08 Upload Package/YOUTUBE_UPLOAD_PACKAGE.md"] },
];

const RISKY_SOURCE_TERMS = [
  "fifa",
  "world cup official",
  "official highlights",
  "tournament highlight",
  "match highlights",
];

function send(res, status, body, headers = {}) {
  const payload = typeof body === "string" ? body : JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": typeof body === "string" ? "text/plain; charset=utf-8" : "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  res.end(payload);
}

function safeResolve(rel = "") {
  const resolved = path.resolve(WORKSPACE_ROOT, rel);
  if (!resolved.startsWith(WORKSPACE_ROOT)) {
    throw new Error("Path is outside the channel workspace.");
  }
  return resolved;
}

function publicPath(urlPath) {
  const clean = decodeURIComponent(urlPath.split("?")[0]);
  const file = clean === "/" ? "index.html" : clean.replace(/^\/+/, "");
  const resolved = path.resolve(PUBLIC_ROOT, file);
  if (!resolved.startsWith(PUBLIC_ROOT)) return null;
  return resolved;
}

async function exists(target) {
  try {
    await fsp.access(target);
    return true;
  } catch {
    return false;
  }
}

async function countFiles(folder) {
  if (!(await exists(folder))) return 0;
  let count = 0;
  const entries = await fsp.readdir(folder, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(folder, entry.name);
    if (entry.isDirectory()) count += await countFiles(full);
    if (entry.isFile() && entry.name !== ".gitkeep") count += 1;
  }
  return count;
}

function videoSlug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

async function scanVideoFolder(absPath) {
  const rel = path.relative(WORKSPACE_ROOT, absPath).replace(/\\/g, "/");
  const name = path.basename(absPath);
  const stageStatuses = [];
  for (const stage of STAGES) {
    let done = false;
    if (stage.files) {
      done = await Promise.all(stage.files.map((f) => exists(path.join(absPath, f)))).then((vals) => vals.some(Boolean));
    }
    if (stage.folders) {
      const counts = await Promise.all(stage.folders.map((f) => countFiles(path.join(absPath, f))));
      done = counts.some((n) => n > 0);
    }
    stageStatuses.push({ ...stage, done });
  }
  const progress = Math.round((stageStatuses.filter((s) => s.done).length / stageStatuses.length) * 100);
  const docs = [];
  for (const [file, label] of DOCS) {
    const abs = path.join(absPath, file);
    docs.push({
      file,
      label,
      exists: await exists(abs),
      relPath: path.join(rel, file).replace(/\\/g, "/"),
    });
  }
  return { name, relPath: rel, progress, stages: stageStatuses, docs };
}

async function listVideos() {
  const candidates = [];
  const rootEntries = await fsp.readdir(WORKSPACE_ROOT, { withFileTypes: true });
  for (const entry of rootEntries) {
    if (entry.isDirectory() && /^Video \d+/.test(entry.name)) {
      candidates.push(path.join(WORKSPACE_ROOT, entry.name));
    }
  }
  const videosRoot = path.join(WORKSPACE_ROOT, "Videos");
  if (await exists(videosRoot)) {
    const entries = await fsp.readdir(videosRoot, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) candidates.push(path.join(videosRoot, entry.name));
    }
  }
  const videos = [];
  for (const folder of candidates) videos.push(await scanVideoFolder(folder));
  return videos.sort((a, b) => a.name.localeCompare(b.name));
}

async function listAssets(relPath) {
  const abs = safeResolve(relPath);
  if (!(await exists(abs))) return [];
  const entries = await fsp.readdir(abs, { withFileTypes: true });
  const rows = [];
  for (const entry of entries) {
    const full = path.join(abs, entry.name);
    const rel = path.relative(WORKSPACE_ROOT, full).replace(/\\/g, "/");
    if (entry.isDirectory()) {
      rows.push({ name: entry.name, type: "folder", relPath: rel, size: null });
    } else if (entry.name !== ".gitkeep") {
      const stat = await fsp.stat(full);
      rows.push({ name: entry.name, type: path.extname(entry.name).slice(1) || "file", relPath: rel, size: stat.size });
    }
  }
  return rows.sort((a, b) => (a.type === "folder" ? -1 : 1) - (b.type === "folder" ? -1 : 1) || a.name.localeCompare(b.name));
}

async function readJson(req) {
  let body = "";
  for await (const chunk of req) body += chunk;
  return body ? JSON.parse(body) : {};
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

async function readTextIfExists(abs) {
  return (await exists(abs)) ? await fsp.readFile(abs, "utf8") : "";
}

async function writeProjectFile(videoAbs, rel, content) {
  const target = path.join(videoAbs, rel);
  await fsp.mkdir(path.dirname(target), { recursive: true });
  await fsp.writeFile(target, content, "utf8");
  return path.relative(WORKSPACE_ROOT, target).replace(/\\/g, "/");
}

async function getVideoByRel(relPath) {
  const abs = safeResolve(relPath);
  if (!(await exists(abs))) throw new Error("Video folder not found.");
  return abs;
}

async function gatherProjectFacts(videoAbs) {
  const script = await readTextIfExists(path.join(videoAbs, "03 script.md"));
  const idea = await readTextIfExists(path.join(videoAbs, "01 idea brief.md"));
  const capcutUpload = await readTextIfExists(path.join(videoAbs, "CapCut Workflow", "08 Upload Package", "YOUTUBE_UPLOAD_PACKAGE.md"));
  const titleMatch =
    script.match(/## Working Title\s+([\s\S]*?)(?:\n##|\n#|$)/i) ||
    capcutUpload.match(/## Title\s+([\s\S]*?)(?:\n##|\n#|$)/i);
  const title = (titleMatch?.[1] || path.basename(videoAbs)).trim().split("\n")[0].trim();
  return { title, script, idea, capcutUpload };
}

async function walkFiles(abs, matcher = () => true) {
  if (!(await exists(abs))) return [];
  const rows = [];
  for (const entry of await fsp.readdir(abs, { withFileTypes: true })) {
    const full = path.join(abs, entry.name);
    if (entry.isDirectory()) rows.push(...(await walkFiles(full, matcher)));
    if (entry.isFile() && matcher(full)) rows.push(full);
  }
  return rows;
}

async function runCopyrightAudit(videoAbs) {
  const files = await walkFiles(videoAbs, (full) => /\.(md|csv|txt|mp4|mov|mkv)$/i.test(full));
  const findings = [];
  for (const file of files) {
    const rel = path.relative(videoAbs, file).replace(/\\/g, "/");
    const lowerName = rel.toLowerCase();
    let text = "";
    if (/\.(md|csv|txt)$/i.test(file)) text = (await readTextIfExists(file)).toLowerCase();
    const hits = RISKY_SOURCE_TERMS.filter((term) => lowerName.includes(term) || text.includes(term));
    if (hits.length) {
      const status = /do not use|claimed|copyright claim|fifa claim/i.test(text) || /do not use|claimed/i.test(lowerName)
        ? "Already flagged"
        : "Needs review";
      findings.push({ rel, hits: [...new Set(hits)].join(", "), status });
    }
  }
  const rows = findings.length
    ? findings.map((f) => `| ${f.rel} | ${f.hits} | ${f.status} |`).join("\n")
    : "| No risky terms found | - | Clear |";
  const content = `# Copyright Audit\n\nGenerated: ${todayIso()}\n\n## Rule\n\nFIFA-sourced and official tournament highlight clips are high-risk for this channel. Prefer original graphics, federation/training footage, press clips, or safe b-roll replacements.\n\n## Findings\n\n| File | Risk Terms | Status |\n|---|---|---|\n${rows}\n\n## Editor Instruction\n\nBefore export, confirm no file marked as claimed, FIFA-sourced, or do-not-use appears in the final CapCut timeline.\n`;
  const relPath = await writeProjectFile(videoAbs, "CapCut Workflow/07 Edit Guides/COPYRIGHT_AUDIT.md", content);
  return { message: "Copyright audit generated.", relPath, findings: findings.length };
}

async function refreshCapCutPackage(videoAbs) {
  const { title } = await gatherProjectFacts(videoAbs);
  const workflow = path.join(videoAbs, "CapCut Workflow");
  const dirs = [
    "01 Voiceover",
    "02 Narrative Inserts",
    "03 Broll - Safe",
    "04 Do Not Use - Claimed",
    "05 Graphics",
    "06 Thumbnail",
    "07 Edit Guides",
    "08 Upload Package",
  ];
  for (const dir of dirs) await fsp.mkdir(path.join(workflow, dir), { recursive: true });

  const readme = `# CapCut Workflow\n\nProject: ${title}\n\n## Editing Rule\n\nThe voiceover is the spine. Narrative inserts prove claims. B-roll supports the voiceover. FIFA-sourced clips are high-risk and should be replaced with graphics or safer sources.\n\n## Import Order\n\n1. Voiceover\n2. Narrative inserts\n3. Safe muted b-roll\n4. Graphics\n5. Thumbnail\n6. Upload package\n\n## Export\n\n- Format: MP4\n- Canvas: 16:9\n- Resolution: 1920x1080\n- Upload: Unlisted first, then check copyright screen\n`;
  await writeProjectFile(videoAbs, "CapCut Workflow/README.md", readme);

  const rules = `# CapCut Asset Rules\n\nGenerated: ${todayIso()}\n\n## Use First\n\n- Narrative inserts that prove specific voiceover claims.\n- Muted safe b-roll under narration.\n- Original graphics for stats, timelines, fixture cards, and copyright-safe replacements.\n\n## Avoid\n\n- FIFA clips\n- Long official match highlights\n- Any asset that previously triggered a YouTube claim\n\n## Final Timeline Check\n\n- B-roll muted\n- Voiceover clear\n- No claimed FIFA footage\n- Captions readable at mobile size\n`;
  const rulesPath = await writeProjectFile(videoAbs, "CapCut Workflow/07 Edit Guides/CAPCUT_ASSET_RULES.md", rules);
  return { message: "CapCut package refreshed.", relPath: rulesPath };
}

async function refreshUploadPackage(videoAbs) {
  const { title, script } = await gatherProjectFacts(videoAbs);
  const description = title.toLowerCase().includes("norway")
    ? "Norway are back at the World Cup, and this is not just a feel-good qualification story. This video breaks down why Norway's squad profile, qualifying run, and attacking weapons make them one of the most uncomfortable teams in the tournament."
    : "A football analysis video built around the strongest story, proof moments, and tactical stakes for this topic.";
  const tags = title.toLowerCase().includes("norway")
    ? "Norway football, Norway World Cup, Erling Haaland, Martin Odegaard, Alexander Sorloth, World Cup 2026, football analysis, football documentary, Norway tactics"
    : "football analysis, football documentary, soccer analysis, football tactics, YouTube football";
  const chaptersHint = script ? "Use the final CapCut timeline to add exact chapter timestamps after export." : "Add chapters after script and final export are ready.";
  const content = `# YouTube Upload Package\n\nGenerated: ${todayIso()}\n\n## Title\n\n${title}\n\n## Description\n\n${description}\n\n## Tags\n\n${tags}\n\n## Thumbnail\n\nUse the final approved thumbnail in the project thumbnail folder.\n\n## Chapters\n\n${chaptersHint}\n\n## Final Upload Checklist\n\n- Export in 1920x1080.\n- Upload as unlisted first.\n- Check YouTube copyright screen.\n- Confirm no FIFA-claimed clips are in the final edit.\n- Confirm title and thumbnail match the same promise.\n- Publish only after copyright status is clean enough for the channel goal.\n`;
  const relPath = await writeProjectFile(videoAbs, "CapCut Workflow/08 Upload Package/YOUTUBE_UPLOAD_PACKAGE.md", content);
  return { message: "Upload package refreshed.", relPath };
}

async function generateProductionSummary(videoAbs) {
  const facts = await gatherProjectFacts(videoAbs);
  const scanned = await scanVideoFolder(videoAbs);
  const completed = scanned.stages.filter((s) => s.done).map((s) => s.label).join(", ");
  const pending = scanned.stages.filter((s) => !s.done).map((s) => s.label).join(", ") || "None";
  const content = `# Production Summary\n\nGenerated: ${todayIso()}\n\n## Video\n\n${facts.title}\n\n## Current Progress\n\n${scanned.progress}% pipeline ready.\n\n## Completed\n\n${completed || "None"}\n\n## Still Needed\n\n${pending}\n\n## Default Workflow\n\nCapCut-first. Descript is not part of the default production path.\n\n## Copyright Rule\n\nAvoid FIFA-sourced clips and official tournament highlight footage unless deliberately reviewed. Prefer original graphics, safe b-roll, training footage, press clips, and transformed analysis visuals.\n\n## Next Best Action\n\nIf the edit is not complete, open the CapCut Workflow folder and follow the edit map. If the edit is complete, export, upload unlisted, and check the YouTube copyright screen before publishing.\n`;
  const relPath = await writeProjectFile(videoAbs, "00 production summary.md", content);
  return { message: "Production summary generated.", relPath };
}

async function runAction(action, videoRelPath) {
  const videoAbs = await getVideoByRel(videoRelPath);
  if (action === "copyright-audit") return runCopyrightAudit(videoAbs);
  if (action === "capcut-package") return refreshCapCutPackage(videoAbs);
  if (action === "upload-package") return refreshUploadPackage(videoAbs);
  if (action === "production-summary") return generateProductionSummary(videoAbs);
  throw new Error("Unknown action.");
}

async function ensureVideoSkeleton(title) {
  const root = path.join(WORKSPACE_ROOT, "Videos");
  await fsp.mkdir(root, { recursive: true });
  const folder = path.join(root, videoSlug(title || "untitled-video"));
  await fsp.mkdir(folder, { recursive: true });
  await fsp.mkdir(path.join(folder, "assets", "editor_package", "narrative_inserts"), { recursive: true });
  await fsp.mkdir(path.join(folder, "assets", "editor_package", "broll"), { recursive: true });
  await fsp.mkdir(path.join(folder, "assets", "voiceover"), { recursive: true });
  await fsp.mkdir(path.join(folder, "CapCut Workflow", "07 Edit Guides"), { recursive: true });
  await fsp.mkdir(path.join(folder, "CapCut Workflow", "08 Upload Package"), { recursive: true });

  const templates = {
    "01 idea brief.md": `# ${title}\n\n## Hook\n\n## Why this can work\n\n## Target audience\n\n## Competitor angle\n\n## Packaging notes\n`,
    "02 research dossier.md": `# Research Dossier\n\n## Core claim\n\n## Facts to verify\n\n## Sources\n\n## Risky claims\n\n## Strongest proof moments\n`,
    "03 script.md": `# Script\n\n## Working Title\n${title}\n\n## Cold Open\n\n## Full Voiceover\n`,
    "04 clip map.csv": `"Order","Voiceover Cue","Asset Needed","Type","Source Lead","Status","Notes"\n`,
    "05 clip sourcing plan.md": `# Clip Sourcing Plan\n\n## Narrative inserts first\n\n## B-roll second\n\n## Copyright risk notes\n`,
    "06 asset acquisition log.md": `# Asset Acquisition Log\n\n## Safe assets\n\n## Do not use\n`,
    "07 edit brief.md": `# Edit Brief\n\n## Tone\n\n## CapCut notes\n\n## Caption style\n`,
    "CapCut Workflow/README.md": `# CapCut Workflow\n\nUse this folder as the editor command center for ${title}.\n`,
    "CapCut Workflow/08 Upload Package/YOUTUBE_UPLOAD_PACKAGE.md": `# YouTube Upload Package\n\n## Title\n${title}\n\n## Description\n\n## Tags\n\n## Thumbnail\n\n## Final checklist\n- Upload unlisted first.\n- Check copyright screen before publishing.\n`,
  };
  for (const [file, content] of Object.entries(templates)) {
    const target = path.join(folder, file);
    if (!(await exists(target))) await fsp.writeFile(target, content, "utf8");
  }
  return scanVideoFolder(folder);
}

async function handleApi(req, res, pathname) {
  if (pathname === "/api/videos" && req.method === "GET") return send(res, 200, { videos: await listVideos() });

  if (pathname === "/api/video" && req.method === "GET") {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const rel = url.searchParams.get("path");
    if (!rel) return send(res, 400, { error: "Missing path." });
    return send(res, 200, { video: await scanVideoFolder(safeResolve(rel)) });
  }

  if (pathname === "/api/assets" && req.method === "GET") {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    return send(res, 200, { assets: await listAssets(url.searchParams.get("path") || "") });
  }

  if (pathname === "/api/doc" && req.method === "GET") {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const rel = url.searchParams.get("path");
    if (!rel) return send(res, 400, { error: "Missing path." });
    const abs = safeResolve(rel);
    const content = (await exists(abs)) ? await fsp.readFile(abs, "utf8") : "";
    return send(res, 200, { relPath: rel, content });
  }

  if (pathname === "/api/doc" && req.method === "PUT") {
    const body = await readJson(req);
    if (!body.path) return send(res, 400, { error: "Missing path." });
    const abs = safeResolve(body.path);
    await fsp.mkdir(path.dirname(abs), { recursive: true });
    await fsp.writeFile(abs, body.content || "", "utf8");
    return send(res, 200, { ok: true });
  }

  if (pathname === "/api/create-video" && req.method === "POST") {
    const body = await readJson(req);
    if (!body.title) return send(res, 400, { error: "Missing title." });
    return send(res, 200, { video: await ensureVideoSkeleton(body.title) });
  }

  if (pathname === "/api/open" && req.method === "POST") {
    const body = await readJson(req);
    const abs = safeResolve(body.path || "");
    if (process.platform === "win32") {
      spawn("explorer.exe", [abs], { detached: true, stdio: "ignore" }).unref();
    }
    return send(res, 200, { ok: true });
  }

  if (pathname === "/api/action" && req.method === "POST") {
    const body = await readJson(req);
    if (!body.path || !body.action) return send(res, 400, { error: "Missing action or path." });
    const result = await runAction(body.action, body.path);
    return send(res, 200, { ok: true, ...result });
  }

  return send(res, 404, { error: "Unknown API route." });
}

function contentType(file) {
  const ext = path.extname(file).toLowerCase();
  return {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
  }[ext] || "application/octet-stream";
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    if (url.pathname.startsWith("/api/")) return await handleApi(req, res, url.pathname);
    const file = publicPath(url.pathname);
    if (!file || !(await exists(file))) return send(res, 404, "Not found");
    const data = await fsp.readFile(file);
    res.writeHead(200, { "Content-Type": contentType(file), "Cache-Control": "no-store" });
    res.end(data);
  } catch (err) {
    send(res, 500, { error: err.message || "Server error" });
  }
});

server.listen(PORT, () => {
  console.log(`Football Channel Studio running at http://localhost:${PORT}`);
});
