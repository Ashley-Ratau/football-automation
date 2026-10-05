const state = {
  videos: [],
  selected: null,
  tab: "overview",
  docPath: null,
  docContent: "",
  assets: {},
  message: "",
  actionMessage: "",
};

const tabs = [
  ["overview", "Overview"],
  ["planning", "Planning"],
  ["script", "Script"],
  ["assets", "Assets"],
  ["capcut", "CapCut"],
  ["actions", "Actions"],
  ["upload", "Upload"],
];

const api = async (url, options) => {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
};

function fmtSize(n) {
  if (n == null) return "";
  if (n > 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`;
  if (n > 1024) return `${Math.round(n / 1024)} KB`;
  return `${n} B`;
}

function escapeHtml(text = "") {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function loadVideos() {
  const data = await api("/api/videos");
  state.videos = data.videos;
  if (!state.selected && state.videos.length) state.selected = state.videos[0];
  if (state.selected) {
    const fresh = state.videos.find((v) => v.relPath === state.selected.relPath);
    if (fresh) state.selected = fresh;
  }
  render();
}

async function selectVideo(relPath) {
  const data = await api(`/api/video?path=${encodeURIComponent(relPath)}`);
  state.selected = data.video;
  state.docPath = null;
  state.docContent = "";
  state.assets = {};
  render();
}

async function createVideo() {
  const input = document.querySelector("#newTitle");
  const title = input.value.trim();
  if (!title) return;
  const data = await api("/api/create-video", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
  input.value = "";
  state.selected = data.video;
  await loadVideos();
}

async function openFolder(relPath) {
  await api("/api/open", { method: "POST", body: JSON.stringify({ path: relPath }) });
}

async function runWorkflowAction(action) {
  state.actionMessage = "Working...";
  render();
  try {
    const data = await api("/api/action", {
      method: "POST",
      body: JSON.stringify({ action, path: state.selected.relPath }),
    });
    state.actionMessage = data.message || "Done";
    await selectVideo(state.selected.relPath);
    state.tab = "actions";
    if (data.relPath) await loadDoc(data.relPath);
  } catch (err) {
    state.actionMessage = err.message;
    render();
  }
}

async function loadDoc(relPath) {
  const data = await api(`/api/doc?path=${encodeURIComponent(relPath)}`);
  state.docPath = data.relPath;
  state.docContent = data.content;
  render();
}

async function saveDoc() {
  const text = document.querySelector("#docEditor")?.value ?? state.docContent;
  await api("/api/doc", {
    method: "PUT",
    body: JSON.stringify({ path: state.docPath, content: text }),
  });
  state.docContent = text;
  state.message = "Saved";
  await selectVideo(state.selected.relPath);
  setTimeout(() => {
    state.message = "";
    render();
  }, 1200);
}

async function loadAssets(key, relPath) {
  const data = await api(`/api/assets?path=${encodeURIComponent(relPath)}`);
  state.assets[key] = data.assets;
  render();
}

function docPanel(filter) {
  const docs = state.selected.docs.filter((d) => !filter || filter(d));
  return `
    <div class="panel">
      <div class="panel-head">
        <h3>Production Docs</h3>
        ${state.message ? `<span class="pill ok">${state.message}</span>` : ""}
      </div>
      <div class="panel-body">
        <div class="doc-list">
          ${docs
            .map(
              (d) => `
                <button class="doc-row ${state.docPath === d.relPath ? "active" : ""}" onclick="loadDoc('${d.relPath.replaceAll("'", "\\'")}')">
                  <span>${d.label}</span>
                  <small class="pill ${d.exists ? "ok" : "warn"}">${d.exists ? "Ready" : "Blank"}</small>
                </button>
              `
            )
            .join("")}
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head">
        <h3>${state.docPath ? state.docPath.split("/").pop() : "Editor"}</h3>
        <button class="solid" ${state.docPath ? "" : "disabled"} onclick="saveDoc()">Save</button>
      </div>
      <textarea id="docEditor" class="editor" placeholder="Open a document to edit it here.">${escapeHtml(state.docContent)}</textarea>
    </div>
  `;
}

function assetPanel(title, key, relPath, note = "") {
  const rows = state.assets[key];
  if (!rows) setTimeout(() => loadAssets(key, relPath), 0);
  return `
    <div class="panel">
      <div class="panel-head">
        <h3>${title}</h3>
        <button class="ghost" onclick="openFolder('${relPath.replaceAll("'", "\\'")}')">Open</button>
      </div>
      <div class="panel-body">
        ${note ? `<p class="path">${note}</p>` : ""}
        <div class="asset-list">
          ${(rows || [])
            .map(
              (a) => `
                <div class="asset-row">
                  <span>${a.name}</span>
                  <small class="pill ${a.relPath.includes("Do Not Use") || a.name.includes("1998") || a.name.includes("iraq") ? "warn" : ""}">${a.type}${a.size ? ` · ${fmtSize(a.size)}` : ""}</small>
                </div>
              `
            )
            .join("") || `<div class="notice">No files found yet.</div>`}
        </div>
      </div>
    </div>
  `;
}

function overview() {
  return `
    <div class="grid">
      <div class="panel">
        <div class="panel-head"><h3>Production Pipeline</h3><span class="pill ok">${state.selected.progress}% complete</span></div>
        <div class="panel-body">
          <div class="stage-grid">
            ${state.selected.stages
              .map(
                (s) => `
                  <div class="stage ${s.done ? "done" : ""}">
                    <b>${s.label}</b>
                    <span class="pill ${s.done ? "ok" : "warn"}">${s.done ? "Ready" : "Needs work"}</span>
                  </div>
                `
              )
              .join("")}
          </div>
        </div>
      </div>
      <div>
        <div class="notice">
          <strong>Channel rule</strong>
          CapCut is the default editing workflow. Narrative inserts first, muted b-roll second, graphics whenever copyright risk is high.
        </div>
        <br />
        <div class="notice">
          <strong>Copyright guardrail</strong>
          FIFA-sourced clips are high-risk. Use original graphics, federation/training footage, press clips, or safe b-roll replacements.
        </div>
      </div>
    </div>
  `;
}

function planning() {
  return `<div class="grid">${docPanel((d) => ["01 idea brief.md", "02 research dossier.md", "04 clip map.csv", "05 clip sourcing plan.md"].includes(d.file))}</div>`;
}

function script() {
  return `<div class="grid">${docPanel((d) => ["03 script.md", "08 voiceover log.md"].includes(d.file))}</div>`;
}

function assets() {
  const base = state.selected.relPath;
  return `
    <div class="split">
      ${assetPanel("Narrative Inserts", "narr", `${base}/assets/editor_package/narrative_inserts`, "Proof clips and graphics that belong at exact voiceover moments.")}
      ${assetPanel("B-roll", "broll", `${base}/assets/editor_package/broll`, "Muted supporting clips. Avoid FIFA-claimed assets.")}
    </div>
  `;
}

function capcut() {
  const base = state.selected.relPath;
  return `
    <div class="split">
      ${assetPanel("CapCut Workflow", "capcut", `${base}/CapCut Workflow`, "Editor command center: edit map, asset rules, and upload package.")}
      <div class="panel">
        <div class="panel-head"><h3>CapCut Build Checklist</h3></div>
        <div class="panel-body checklist">
          ${[
            "Import Cedar voiceover first",
            "Place narrative inserts at the mapped voiceover cues",
            "Use only safe muted b-roll under narration",
            "Replace FIFA 1998/Iraq footage with graphics",
            "Use 1920x1080 graphics and bold captions",
            "Export 1080p and upload unlisted first",
          ]
            .map((x) => `<label class="check"><input type="checkbox" /> <span>${x}</span></label>`)
            .join("")}
        </div>
      </div>
    </div>
  `;
}

function actions() {
  const cards = [
    {
      id: "production-summary",
      title: "Generate Production Summary",
      body: "Creates a top-level summary of the current video status, completed stages, pending tasks, and next best action.",
      button: "Create Summary",
    },
    {
      id: "copyright-audit",
      title: "Run Copyright Audit",
      body: "Scans local project docs and filenames for high-risk source terms like FIFA and official highlights, then writes an editor-facing audit.",
      button: "Run Audit",
    },
    {
      id: "capcut-package",
      title: "Refresh CapCut Package",
      body: "Rebuilds the CapCut workflow README and asset rules so the editor has a clean, current handoff.",
      button: "Refresh CapCut",
    },
    {
      id: "upload-package",
      title: "Refresh Upload Package",
      body: "Creates or updates the YouTube title, description, tags, thumbnail notes, chapters note, and final upload checklist.",
      button: "Refresh Upload",
    },
  ];
  return `
    <div class="grid">
      <div class="panel">
        <div class="panel-head">
          <h3>Action Center</h3>
          ${state.actionMessage ? `<span class="pill ok">${state.actionMessage}</span>` : ""}
        </div>
        <div class="panel-body action-grid">
          ${cards
            .map(
              (card) => `
                <div class="action-card">
                  <h4>${card.title}</h4>
                  <p>${card.body}</p>
                  <button class="solid" onclick="runWorkflowAction('${card.id}')">${card.button}</button>
                </div>
              `
            )
            .join("")}
        </div>
      </div>
      <div class="panel">
        <div class="panel-head">
          <h3>${state.docPath ? state.docPath.split("/").pop() : "Generated Output"}</h3>
          <button class="solid" ${state.docPath ? "" : "disabled"} onclick="saveDoc()">Save</button>
        </div>
        <textarea id="docEditor" class="editor" placeholder="Run an action to generate or open a workflow file.">${escapeHtml(state.docContent)}</textarea>
      </div>
    </div>
  `;
}

function upload() {
  const uploadDoc = state.selected.docs.find((d) => d.relPath.endsWith("YOUTUBE_UPLOAD_PACKAGE.md"));
  return `
    <div class="grid">
      <div class="panel">
        <div class="panel-head"><h3>Upload Controls</h3></div>
        <div class="panel-body">
          <p>This screen is for the final title, description, tags, thumbnail, and publish checks. YouTube upload automation can be connected here later once the channel API access is ready.</p>
          <button class="solid" onclick="loadDoc('${state.selected.relPath}/CapCut Workflow/08 Upload Package/YOUTUBE_UPLOAD_PACKAGE.md')">Open Upload Package</button>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head">
          <h3>${state.docPath ? state.docPath.split("/").pop() : "Upload Package"}</h3>
          <button class="solid" ${state.docPath ? "" : "disabled"} onclick="saveDoc()">Save</button>
        </div>
        <textarea id="docEditor" class="editor" placeholder="Open the upload package to edit metadata.">${escapeHtml(state.docContent)}</textarea>
      </div>
    </div>
  `;
}

function mainContent() {
  if (!state.selected) return `<div class="empty">Create or select a video project to begin.</div>`;
  const view = { overview, planning, script, assets, capcut, actions, upload }[state.tab] || overview;
  return `
    <main class="main">
      <div class="topbar">
        <div class="title-block">
          <h2>${state.selected.name}</h2>
          <p>${state.selected.relPath}</p>
        </div>
        <div class="actions">
          <button class="ghost" onclick="openFolder('${state.selected.relPath.replaceAll("'", "\\'")}')">Open Folder</button>
          <button class="solid" onclick="loadVideos()">Refresh</button>
        </div>
      </div>
      <nav class="tabs">
        ${tabs
          .map(([id, label]) => `<button class="tab ${state.tab === id ? "active" : ""}" onclick="state.tab='${id}'; render();">${label}</button>`)
          .join("")}
      </nav>
      ${view()}
    </main>
  `;
}

function render() {
  document.querySelector("#app").innerHTML = `
    <div class="app">
      <aside class="sidebar">
        <div class="brand">
          <div class="mark">FC</div>
          <div>
            <h1>Football Channel Studio</h1>
            <p>Local production command center</p>
          </div>
        </div>
        <div class="new-video">
          <input id="newTitle" placeholder="New video title" />
          <button onclick="createVideo()">Create Video</button>
        </div>
        <div class="video-list">
          ${state.videos
            .map(
              (v) => `
                <button class="video-card ${state.selected?.relPath === v.relPath ? "active" : ""}" onclick="selectVideo('${v.relPath.replaceAll("'", "\\'")}')">
                  <strong>${v.name}</strong>
                  <div class="progress"><div class="bar" style="width:${v.progress}%"></div></div>
                  <small>${v.progress}% pipeline ready</small>
                </button>
              `
            )
            .join("")}
        </div>
      </aside>
      ${mainContent()}
    </div>
  `;
}

loadVideos().catch((err) => {
  document.querySelector("#app").innerHTML = `<pre>${escapeHtml(err.message)}</pre>`;
});
