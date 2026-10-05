from __future__ import annotations

import argparse
import dataclasses
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
STATE_DIR = WORK / "automation_state"
STATE_FILE = STATE_DIR / "football_short_state.json"
LOCK_FILE = STATE_DIR / "football_short.lock"
OPENAI_MODEL = os.environ.get("OPENAI_TEXT_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.environ.get("OPENAI_TEXT_TEMPERATURE", "0.75"))
ELEVENLABS_SPEED = float(os.environ.get("FOOTBALL_VOICE_SPEED", "1.2"))
VOICE_ID_ENV = "ELEVENLABS_VOICE_ID"
OPENAI_KEY_ENV = "OPENAI_API_KEY"

FFMPEG = Path(
    r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
)
BUNDLED_PYTHON = Path(
    r"C:\Users\Wendy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)
YTDLP = shutil.which("yt-dlp") or r"C:\Users\Wendy\AppData\Local\Programs\Python\Python312\Scripts\yt-dlp.exe"

FOOTBALL_QUERIES = [
    "football",
    "world cup football",
    "uefa football",
    "premier league football",
    "champions league football",
    "real madrid football",
    "barcelona football",
    "england football",
    "cristiano ronaldo football",
    "pep guardiola football",
]

SOCCER_KEYWORDS = {
    "world cup",
    "uefa",
    "champions league",
    "premier league",
    "la liga",
    "serie a",
    "bundesliga",
    "ligue 1",
    "fifa",
    "real madrid",
    "barcelona",
    "manchester city",
    "manchester united",
    "liverpool",
    "arsenal",
    "chelsea",
    "spain",
    "portugal",
    "france",
    "germany",
    "england",
    "ronaldo",
    "messi",
    "haaland",
    "yamal",
    "odegaard",
}

AMERICAN_FOOTBALL_BLACKLIST = {
    "college",
    "nfl",
    "kickoff",
    "kick off",
    "kickoff time",
    "auburn",
    "samford",
    "texas",
    "tennessee",
    "alabama",
    "sec football",
    "football at",
    "athletics",
    "game time",
    "schedule",
    "scoreboard",
    "quarterback",
    "touchdown",
    "linebacker",
}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "what",
    "when",
    "into",
    "about",
    "after",
    "before",
    "have",
    "has",
    "had",
    "will",
    "not",
    "are",
    "was",
    "were",
    "they",
    "them",
    "his",
    "her",
    "our",
    "your",
    "their",
}


@dataclasses.dataclass
class NewsItem:
    query: str
    title: str
    link: str
    source: str
    published: str


def run(cmd: list[str], *, cwd: Path | None = None, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
    )


def ensure_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_env_files() -> None:
    for env_path in [ROOT / ".env.local", WORK / "secrets" / ".env.local"]:
        if not env_path.exists():
            continue
        for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


def env(name: str, default: str = "") -> str:
    load_env_files()
    return os.environ.get(name, default).strip()


def ffmpeg_exe() -> str:
    return str(FFMPEG if FFMPEG.exists() else "ffmpeg")


def bundled_python() -> str:
    return str(BUNDLED_PYTHON if BUNDLED_PYTHON.exists() else sys.executable)


def slugify(text: str, limit: int = 72) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:limit].strip("-") or "football-short"


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", normalize(text)) if w not in STOPWORDS}


def score_similarity(a: str, b: str) -> float:
    aw = words(a)
    bw = words(b)
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / len(aw | bw)


def is_soccer_story(text: str) -> bool:
    n = normalize(text)
    if any(bad in n for bad in AMERICAN_FOOTBALL_BLACKLIST):
        return False
    return any(good in n for good in SOCCER_KEYWORDS)


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"used_titles": [], "runs": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"used_titles": [], "runs": []}


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def acquire_lock() -> None:
    ensure_dirs()
    if LOCK_FILE.exists():
        try:
            payload = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
            started = float(payload.get("started_at", 0))
            if time.time() - started < 60 * 60 * 5:
                raise SystemExit("Another automation run appears to be active. Exiting.")
        except Exception:
            pass
    LOCK_FILE.write_text(json.dumps({"started_at": time.time(), "pid": os.getpid()}, indent=2), encoding="utf-8")


def release_lock() -> None:
    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink()
        except Exception:
            pass


def next_video_number() -> int:
    pattern = re.compile(r"^Video\s+(\d+)\s+-")
    highest = 0
    for path in ROOT.iterdir():
        if not path.is_dir():
            continue
        m = pattern.match(path.name)
        if m:
            highest = max(highest, int(m.group(1)))
    return highest + 1


def safe_title_fragment(text: str, limit: int = 72) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "", text).strip()
    return text[:limit].strip()


def http_get(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def openai_chat_json(system_prompt: str, user_prompt: str, model: str = OPENAI_MODEL) -> dict[str, Any]:
    api_key = env(OPENAI_KEY_ENV)
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in .env.local.")
    payload = {
        "model": model,
        "temperature": OPENAI_TEMPERATURE,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"OpenAI text request failed: HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}") from exc
    content = data["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise


def fetch_google_news_candidates() -> list[NewsItem]:
    items: list[NewsItem] = []
    for query in FOOTBALL_QUERIES:
        rss_url = (
            "https://news.google.com/rss/search?q="
            + urllib.parse.quote(f"{query} when:1d")
            + "&hl=en-US&gl=US&ceid=US:en"
        )
        try:
            raw = http_get(rss_url, timeout=30)
            root = ET.fromstring(raw)
        except Exception:
            continue
        for item in root.findall(".//item")[:5]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            source = (item.findtext("source") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            if title and link:
                items.append(NewsItem(query=query, title=title, link=link, source=source, published=pub))
    deduped: list[NewsItem] = []
    seen = set()
    for item in items:
        key = normalize(item.title)
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped[:24]


def filter_soccer_candidates(candidates: list[NewsItem]) -> list[NewsItem]:
    filtered = [item for item in candidates if is_soccer_story(item.title)]
    return filtered or candidates


def scan_existing_titles() -> list[str]:
    titles: list[str] = []
    for path in ROOT.iterdir():
        if path.is_dir():
            m = re.match(r"^Video\s+\d+\s+-\s+(.+)$", path.name)
            if m:
                titles.append(m.group(1))
    for upload_record in ROOT.rglob("upload records/*.md"):
        text = upload_record.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if line.startswith("Title:"):
                titles.append(line.split(":", 1)[1].strip())
    state = load_state()
    titles.extend(state.get("used_titles", []))
    # preserve order, remove duplicates
    out = []
    seen = set()
    for title in titles:
        n = normalize(title)
        if n and n not in seen:
            out.append(title)
            seen.add(n)
    return out


def choose_topic_with_openai(candidates: list[NewsItem], existing_titles: list[str]) -> dict[str, Any]:
    candidate_lines = []
    for idx, item in enumerate(candidates, 1):
        candidate_lines.append(
            f"{idx}. {item.title} | source={item.source or item.query} | pub={item.published} | link={item.link}"
        )
    system_prompt = (
        "You are a football YouTube Shorts strategist. "
        "Only choose actual association football / soccer stories, never American college football, NFL, or generic TV schedule items. "
        "Pick one fresh topic from the candidate news items. "
        "The channel style is sharp football essays with warning/prophecy framing. "
        "Use high-quality portrait images as the main B-roll. "
        "Keep every portrait image on screen for 3 seconds or less. "
        "Use at most one or two insert clips, and the first insert should land early. "
        "Avoid duplicate or near-duplicate ideas from the existing titles. "
        "Return JSON only."
    )
    user_prompt = json.dumps(
        {
            "existing_titles": existing_titles[-30:],
            "candidate_news": [
                dataclasses.asdict(item) for item in candidates
            ],
            "requirements": {
                "video_type": "YouTube Short",
                "format": "9:16",
                "goal": "public upload every two hours",
                "voice_style": "serious documentary football narrator",
                "voice_speed": "1.2x",
                "broll_rules": [
                    "use portrait images whenever possible",
                    "keep each image under 3 seconds",
                    "prefer full-frame portraits centered on the subject",
                    "align each image to the exact player/person being mentioned",
                ],
                "insert_rules": [
                    "split the voiceover naturally around the insert clip",
                    "do not mute voiceover underneath the insert; cut to the clip cleanly",
                ],
                "thumbnail_rules": [
                    "generate 3 thumbnail options",
                    "use portrait-style sports thumbnails",
                    "keep them high contrast and realistic",
                ],
            },
        },
        indent=2,
        ensure_ascii=False,
    )
    return openai_chat_json(system_prompt, user_prompt)


def fallback_plan(candidates: list[NewsItem]) -> dict[str, Any]:
    top = candidates[0] if candidates else NewsItem("football", "Football news", "", "news", "")
    title = top.title.replace(" - Google News", "")
    cleaned = re.sub(r"\s+-\s+.*$", "", title)
    short_title = cleaned[:70]
    return {
        "project_title": short_title,
        "folder_title": f"Video {next_video_number():03d} - {safe_title_fragment(short_title)}",
        "upload_title": short_title,
        "description": f"Latest football reaction video about: {short_title}",
        "tags": ["football", "soccer", "shorts", "news"],
        "topic_summary": short_title,
        "script_sections": [
            {
                "id": 1,
                "text": f"This is the latest football story: {short_title}. It looks small on the surface, but it says a lot about where the game is headed.",
                "image_entities": ["Thomas Tuchel", "Pep Guardiola"],
                "insert_after": False,
            },
            {
                "id": 2,
                "text": "The warning here is simple: the biggest stories in football are never just about the headline. They are about power, pressure, and who is getting exposed when the noise gets loud.",
                "image_entities": ["Thomas Tuchel"],
                "insert_after": True,
                "insert_clip_query": "football pundit warning interview",
                "insert_duration": 12,
            },
            {
                "id": 3,
                "text": "That is why the smart move is to watch the people around the story, not just the player in the middle of it.",
                "image_entities": ["Pep Guardiola"],
                "insert_after": False,
            },
        ],
        "thumbnail_options": [
            {
                "headline": "HE KNEW",
                "left_subject": "Thomas Tuchel",
                "center_subject": "football player",
                "right_subject": "",
                "style_notes": "dark, realistic, high contrast",
            },
            {
                "headline": "NO ONE LISTENED",
                "left_subject": "Pep Guardiola",
                "center_subject": "football player",
                "right_subject": "",
                "style_notes": "dark, realistic, warning tone",
            },
            {
                "headline": "THE WARNING",
                "left_subject": "legend",
                "center_subject": "current player",
                "right_subject": "",
                "style_notes": "clean, punchy, realistic",
            },
        ],
    }


def select_plan(candidates: list[NewsItem], existing_titles: list[str]) -> dict[str, Any]:
    candidates = filter_soccer_candidates(candidates)
    if not candidates:
        return fallback_plan([])
    try:
        plan = choose_topic_with_openai(candidates, existing_titles)
    except Exception as exc:
        print(f"[plan] OpenAI selection failed, using fallback: {exc}")
        return fallback_plan(candidates)
    if "script_sections" not in plan:
        return fallback_plan(candidates)
    return plan


def project_dir_for_plan(plan: dict[str, Any]) -> Path:
    folder_title = safe_title_fragment(plan["folder_title"])
    return ROOT / folder_title


def make_dirs(project: Path) -> dict[str, Path]:
    paths = {
        "project": project,
        "voiceover": project / "assets" / "voiceover" / "elevenlabs",
        "voiceover_fast": project / "assets" / "voiceover" / "elevenlabs_1p2x",
        "raw_sources": project / "assets" / "raw_sources",
        "portraits": project / "assets" / "raw_sources" / "portraits",
        "editor_inserts": project / "assets" / "editor_package" / "narrative_inserts",
        "editor_broll": project / "assets" / "editor_package" / "broll_safe" / "short_clips",
        "graphics": project / "assets" / "editor_package" / "graphics",
        "thumbnail": project / "assets" / "thumbnail",
        "capcut_export": project / "final video" / "capcut export",
        "upload_records": project / "final video" / "upload records",
        "instructions": project / "00 instructions",
        "tmp": project / "_tmp",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def render_script_markdown(plan: dict[str, Any]) -> str:
    sections = plan.get("script_sections", [])
    voice_text = "\n\n".join(section["text"].strip() for section in sections if section.get("text"))
    outline = ["# Script Outline", ""]
    for section in sections:
        outline.append(f"- Section {section['id']}: {section['text'][:120].strip()}")
    outline.append("")
    outline.append("# Full Voiceover Script")
    outline.append("")
    outline.append(voice_text)
    return "\n".join(outline)


def make_research_dossier(plan: dict[str, Any], candidates: list[NewsItem], existing_titles: list[str]) -> str:
    lines = ["# Research Dossier", ""]
    lines.append(f"Chosen topic: {plan.get('topic_summary', plan.get('upload_title', 'Football story'))}")
    lines.append("")
    lines.append("## Why this topic")
    lines.append(plan.get("topic_summary", ""))
    lines.append("")
    lines.append("## News candidates reviewed")
    for item in candidates[:10]:
        lines.append(f"- {item.title} ({item.source or item.query})")
    lines.append("")
    lines.append("## Recent titles to avoid")
    for title in existing_titles[-15:]:
        lines.append(f"- {title}")
    lines.append("")
    lines.append("## Production notes")
    lines.append("- Use portrait images as the main B-roll.")
    lines.append("- Keep each image on screen for 3 seconds or less.")
    lines.append("- Cut the voiceover completely during insert clips.")
    lines.append("- Prefer one strong insert clip early in the short.")
    return "\n".join(lines)


def make_upload_metadata(plan: dict[str, Any]) -> str:
    tags = plan.get("tags") or []
    lines = [
        "# Upload Metadata",
        "",
        f"Title: {plan.get('upload_title', plan.get('project_title', 'Football Short'))}",
        "",
        "Description:",
        "",
        plan.get("description", ""),
        "",
        "Tags:",
        "",
        ", ".join(tags),
        "",
        "Privacy:",
        "",
        "public",
    ]
    return "\n".join(lines)


def save_plan_json(project: Path, plan: dict[str, Any], candidates: list[NewsItem]) -> None:
    payload = {
        "plan": plan,
        "news_candidates": [dataclasses.asdict(item) for item in candidates],
    }
    write_markdown(project / "00 instructions" / "plan.json", json.dumps(payload, indent=2, ensure_ascii=False))


def entity_to_slug(entity: str) -> str:
    return slugify(entity, limit=50)


def wikipedia_image_for_entity(entity: str) -> str | None:
    search_terms = [entity, f"{entity} football", f"{entity} portrait"]
    for term in search_terms:
        try:
            query_url = (
                "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&pithumbsize=1200&titles="
                + urllib.parse.quote(term)
            )
            raw = http_get(query_url, timeout=30)
            data = json.loads(raw.decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                thumb = page.get("thumbnail", {})
                source = thumb.get("source")
                if source:
                    return source
        except Exception:
            continue
    return None


def download_image(url: str, out_path: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            out_path.write_bytes(response.read())
        return True
    except Exception:
        return False


def gather_portraits(project_paths: dict[str, Path], plan: dict[str, Any]) -> dict[str, Path]:
    portrait_dir = project_paths["portraits"]
    used: dict[str, Path] = {}
    entities: list[str] = []
    for section in plan.get("script_sections", []):
        entities.extend(section.get("image_entities") or [])
    entities.extend([opt.get("left_subject", "") for opt in plan.get("thumbnail_options", [])])
    entities.extend([opt.get("center_subject", "") for opt in plan.get("thumbnail_options", [])])
    seen = set()
    for entity in entities:
        entity = (entity or "").strip()
        if not entity or entity in seen:
            continue
        seen.add(entity)
        url = wikipedia_image_for_entity(entity)
        if not url:
            continue
        out_path = portrait_dir / f"{entity_to_slug(entity)}.jpg"
        if download_image(url, out_path):
            used[entity] = out_path
    return used


def search_youtube_candidates(query: str, limit: int = 6) -> list[dict[str, Any]]:
    cmd = [
        YTDLP,
        "--flat-playlist",
        "--dump-single-json",
        f"ytsearch{limit}:{query}",
    ]
    try:
        proc = run(cmd, capture=True, check=True)
        data = json.loads(proc.stdout)
    except Exception:
        return []
    entries = data.get("entries") or []
    out = []
    for entry in entries:
        if not entry:
            continue
        out.append(
            {
                "title": entry.get("title") or "",
                "webpage_url": entry.get("webpage_url") or entry.get("url") or "",
                "duration": entry.get("duration") or 0,
                "uploader": entry.get("uploader") or "",
                "channel": entry.get("channel") or "",
            }
        )
    return out


def pick_insert_candidate(query: str, plan: dict[str, Any]) -> dict[str, Any] | None:
    candidates = search_youtube_candidates(query, limit=8)
    if not candidates:
        return None
    keywords = words(query) | words(plan.get("upload_title", "")) | words(plan.get("topic_summary", ""))
    best = None
    best_score = -1.0
    for cand in candidates:
        cand_words = words(cand["title"])
        score = len(keywords & cand_words)
        duration = float(cand.get("duration") or 0)
        if duration and duration < 8:
            score -= 2
        if duration and duration > 90:
            score -= 1
        score += min(duration / 20.0, 2.0)
        if score > best_score:
            best_score = score
            best = cand
    return best


def download_insert_clip(plan: dict[str, Any], project_paths: dict[str, Path]) -> Path | None:
    inserts = plan.get("insert_clips") or []
    if not inserts:
        return None
    first = inserts[0]
    query = first.get("search_query") or first.get("query") or plan.get("upload_title", "")
    pick = pick_insert_candidate(query, plan)
    if not pick or not pick.get("webpage_url"):
        return None
    out_path = project_paths["editor_inserts"] / f"insert_{slugify(query, 50)}.mp4"
    if out_path.exists():
        return out_path
    cmd = [
        YTDLP,
        "-f",
        "bestvideo+bestaudio/best",
        "--merge-output-format",
        "mp4",
        "-o",
        str(out_path),
        pick["webpage_url"],
    ]
    try:
        run(cmd, capture=True)
        return out_path if out_path.exists() else None
    except Exception:
        return None


def ffprobe_duration(path: Path) -> float:
    cmd = [ffmpeg_exe(), "-hide_banner", "-i", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    text = proc.stderr + proc.stdout
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", text)
    if not match:
        raise RuntimeError(f"Could not read duration for {path}")
    h, m, s = match.groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def atempo_filter(speed: float) -> str:
    parts = []
    remaining = speed
    while remaining > 2.0:
        parts.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        parts.append("atempo=0.5")
        remaining /= 0.5
    parts.append(f"atempo={remaining:.4f}")
    return ",".join(parts)


def speed_adjust_mp3(input_path: Path, output_path: Path, speed: float) -> None:
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-i",
        str(input_path),
        "-filter:a",
        atempo_filter(speed),
        "-vn",
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(output_path),
    ]
    run(cmd)


def copy_text_assets(project: Path, plan: dict[str, Any], candidates: list[NewsItem]) -> None:
    write_markdown(project / "01 idea brief.md", f"# Idea Brief\n\n{plan.get('topic_summary', '')}\n")
    write_markdown(project / "02 research dossier.md", make_research_dossier(plan, candidates, scan_existing_titles()))
    write_markdown(project / "03 script.md", render_script_markdown(plan))
    write_markdown(project / "04 upload metadata.md", make_upload_metadata(plan))
    write_markdown(project / "05 clip sourcing plan.md", render_clip_sourcing_plan(plan))
    write_markdown(project / "06 thumbnail options.md", render_thumbnail_options(plan))
    write_markdown(project / "07 edit brief.md", render_edit_brief(plan))


def render_edit_brief(plan: dict[str, Any]) -> str:
    lines = [
        "# Edit Brief",
        "",
        "Use the voiceover as the spine.",
        "Cut the voiceover completely during insert clips.",
        "Use portrait images as the main B-roll.",
        "Keep each portrait image on screen for 3 seconds or less.",
        "Keep the pacing tight and visual.",
        "",
        "## Script Sections",
    ]
    for section in plan.get("script_sections", []):
        lines.append(f"- Section {section['id']}: {section['text'][:120]}")
    return "\n".join(lines)


def render_clip_sourcing_plan(plan: dict[str, Any]) -> str:
    lines = [
        "# Clip Sourcing Plan",
        "",
        "## Narrative inserts",
    ]
    for insert in plan.get("insert_clips", []):
        lines.append(
            f"- After section {insert.get('after_section_id')}: {insert.get('search_query') or insert.get('query')}"
        )
    lines.append("")
    lines.append("## Portrait image targets")
    for section in plan.get("script_sections", []):
        imgs = ", ".join(section.get("image_entities") or [])
        lines.append(f"- Section {section['id']}: {imgs}")
    return "\n".join(lines)


def render_thumbnail_options(plan: dict[str, Any]) -> str:
    lines = ["# Thumbnail Options", ""]
    for idx, opt in enumerate(plan.get("thumbnail_options", []), 1):
        lines.append(f"## Option {idx}")
        for key, value in opt.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines)


def build_text_card(text: str, subtitle: str | None, out_path: Path, accent: str = "#e11d48") -> None:
    img = Image.new("RGB", (1080, 1920), "#07111a")
    draw = ImageDraw.Draw(img)
    draw.rectangle((74, 120, 90, 1520), fill=accent)
    title_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 58)
    body_font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 40)
    draw.text((120, 165), text, fill="white", font=title_font)
    if subtitle:
        draw.text((120, 300), subtitle, fill="#d6dde5", font=body_font)
    img.save(out_path)


def make_fullframe_still(image_path: Path, out_path: Path, duration: float) -> None:
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-t",
        f"{duration:.3f}",
        "-shortest",
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    run(cmd)


def trim_vertical_clip(source: Path, out_path: Path, duration: float) -> None:
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-i",
        str(source),
        "-t",
        f"{duration:.3f}",
        "-vf",
        "scale=-2:1920,crop=1080:1920,setsar=1",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    run(cmd)


def concat_segments(segment_paths: list[Path], out_path: Path) -> None:
    list_path = out_path.parent / "concat_list.txt"
    list_path.write_text("\n".join(f"file '{p.as_posix()}'" for p in segment_paths), encoding="utf-8")
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    run(cmd)


def build_voice_section_segment(
    *,
    project_paths: dict[str, Path],
    section: dict[str, Any],
    audio_path: Path,
    portraits: dict[str, Path],
) -> Path:
    duration = ffprobe_duration(audio_path)
    image_entities = [x for x in section.get("image_entities") or [] if portraits.get(x)]
    image_paths = [portraits[x] for x in image_entities] or list(portraits.values())
    if not image_paths:
        placeholder = project_paths["tmp"] / f"placeholder_{section['id']}.png"
        build_text_card("FOOTBALL CHANNEL", "Automation placeholder", placeholder)
        image_paths = [placeholder]

    stills: list[Path] = []
    remaining = duration
    idx = 0
    while remaining > 0:
        seg_dur = min(3.0, remaining)
        img = image_paths[idx % len(image_paths)]
        part_path = project_paths["tmp"] / f"section_{section['id']}_still_{idx + 1:02d}.mp4"
        make_fullframe_still(img, part_path, seg_dur)
        stills.append(part_path)
        remaining -= seg_dur
        idx += 1

    visual = project_paths["tmp"] / f"section_{section['id']}_visual.mp4"
    concat_segments(stills, visual)
    final_segment = project_paths["tmp"] / f"section_{section['id']}_voice.mp4"
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-i",
        str(visual),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-shortest",
        "-movflags",
        "+faststart",
        str(final_segment),
    ]
    run(cmd)
    return final_segment


def build_insert_segment(project_paths: dict[str, Path], insert_clip: Path, target_duration: float, insert_id: int) -> Path:
    duration = ffprobe_duration(insert_clip)
    use_duration = min(duration, target_duration)
    segment = project_paths["tmp"] / f"insert_{insert_id:02d}.mp4"
    trim_vertical_clip(insert_clip, segment, use_duration)
    return segment


def get_voice_parts(project: Path) -> list[Path]:
    base = project / "assets" / "voiceover" / "elevenlabs"
    return sorted(base.glob("*.mp3"))


def generate_voiceover(project: Path, voice_id: str | None) -> None:
    cmd = [
        bundled_python(),
        str(WORK / "generate_elevenlabs_voiceover.py"),
        "generate",
        "--project",
        str(project),
    ]
    if voice_id:
        cmd.extend(["--voice-id", voice_id])
    cmd.append("--split-paragraphs")
    run(cmd)


def speed_adjust_voiceover(project: Path, speed: float) -> dict[str, Path]:
    src_dir = project / "assets" / "voiceover" / "elevenlabs"
    dst_dir = project / "assets" / "voiceover" / f"elevenlabs_{str(speed).replace('.', 'p')}x"
    dst_dir.mkdir(parents=True, exist_ok=True)
    adjusted: dict[str, Path] = {}
    for mp3 in sorted(src_dir.glob("*.mp3")):
        if "full" in mp3.name:
            continue
        out = dst_dir / mp3.name
        speed_adjust_mp3(mp3, out, speed)
        adjusted[mp3.name] = out
    full_src = src_dir / "voiceover_elevenlabs_full.mp3"
    full_out = dst_dir / "voiceover_elevenlabs_full_1p2x.mp3"
    if full_src.exists():
        speed_adjust_mp3(full_src, full_out, speed)
        adjusted[full_src.name] = full_out
    return adjusted


def create_thumbnail_image(
    *,
    bg_image: Path,
    left_image: Path | None,
    center_image: Path | None,
    right_image: Path | None,
    headline: str,
    out_path: Path,
) -> None:
    base = Image.open(bg_image).convert("RGB")
    bg = ImageOps.fit(base, (1080, 1920), centering=(0.5, 0.5)).filter(ImageFilter.GaussianBlur(radius=18))
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, 1080, 1920), fill=(0, 0, 0, 55))
    od.rectangle((0, 0, 1080, 220), fill=(0, 0, 0, 55))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    def paste_subject(src: Path | None, box: tuple[int, int, int, int], alpha: int = 255) -> None:
        if not src or not src.exists():
            return
        fg = ImageOps.fit(Image.open(src).convert("RGB"), (box[2] - box[0], box[3] - box[1]), centering=(0.5, 0.5))
        if alpha < 255:
            fg = fg.convert("RGBA")
            fg.putalpha(alpha)
        bg.alpha_composite(fg.convert("RGBA"), (box[0], box[1]))

    paste_subject(left_image, (20, 170, 420, 1610), 235)
    paste_subject(center_image, (350, 100, 800, 1680), 255)
    paste_subject(right_image, (670, 170, 1060, 1610), 235)

    draw = ImageDraw.Draw(bg)
    draw.rectangle((0, 1570, 1080, 1920), fill=(0, 0, 0, 0))
    font_big = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 96)
    font_mid = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 56)
    draw.text((70, 70), headline.upper(), fill="white", font=font_big, stroke_width=6, stroke_fill="black")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.convert("RGB").save(out_path)


def build_thumbnail_variants(project: Path, plan: dict[str, Any], portraits: dict[str, Path]) -> Path:
    options = plan.get("thumbnail_options") or []
    thumb_dir = project / "assets" / "thumbnail"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    for idx, option in enumerate(options[:3], 1):
        left = portraits.get(option.get("left_subject", "")) or next(iter(portraits.values()), None)
        center = portraits.get(option.get("center_subject", "")) or next(iter(portraits.values()), None)
        right = portraits.get(option.get("right_subject", "")) or None
        bg = center or left or right
        if not bg:
            continue
        out = thumb_dir / f"thumbnail_{idx}.png"
        create_thumbnail_image(
            bg_image=bg,
            left_image=left,
            center_image=center,
            right_image=right,
            headline=option.get("headline", plan.get("upload_title", "")),
            out_path=out,
        )
        built.append(out)
    primary_index = int(plan.get("primary_thumbnail_index") or 0)
    if built:
        chosen = built[min(primary_index, len(built) - 1)]
        shutil.copy2(chosen, thumb_dir / "thumbnail_primary.png")
        return thumb_dir / "thumbnail_primary.png"
    placeholder = thumb_dir / "thumbnail_primary.png"
    build_text_card(plan.get("upload_title", "FOOTBALL SHORT"), "Automation thumbnail", placeholder, accent="#2563eb")
    return placeholder


def build_final_video(
    project: Path,
    plan: dict[str, Any],
    portraits: dict[str, Path],
    insert_clip: Path | None,
) -> Path:
    section_audio_dir = project / "assets" / "voiceover" / f"elevenlabs_{str(ELEVENLABS_SPEED).replace('.', 'p')}x"
    segments: list[Path] = []
    insert_after = {int(item.get("after_section_id")): item for item in plan.get("insert_clips") or [] if item.get("after_section_id")}

    for section in plan.get("script_sections", []):
        audio_name = f"elevenlabs_part_{int(section['id']):02d}.mp3"
        audio_path = section_audio_dir / audio_name
        if not audio_path.exists():
            # fallback to the unspaced naming convention if the generator changes
            candidates = sorted(section_audio_dir.glob(f"*part_{int(section['id']):02d}.mp3"))
            if candidates:
                audio_path = candidates[0]
        if not audio_path.exists():
            raise RuntimeError(f"Missing voiceover part for section {section['id']}: {audio_path}")
        voice_segment = build_voice_section_segment(
            project_paths=make_dirs(project),
            section=section,
            audio_path=audio_path,
            portraits=portraits,
        )
        segments.append(voice_segment)

        if int(section["id"]) in insert_after and insert_clip and insert_clip.exists():
            insert_plan = insert_after[int(section["id"])]
            target_duration = float(insert_plan.get("target_duration") or 12)
            insert_segment = build_insert_segment(make_dirs(project), insert_clip, target_duration, int(section["id"]))
            segments.append(insert_segment)

    final_path = project / "final video" / "capcut export" / f"{slugify(plan.get('upload_title', 'football-short'))}.mp4"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    concat_segments(segments, final_path)
    return final_path


def upload_youtube(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    *,
    privacy: str = "public",
) -> dict[str, Any]:
    cmd = [
        bundled_python(),
        str(WORK / "youtube_oauth_tool.py"),
        "upload",
        "--file",
        str(video_path),
        "--title",
        title,
        "--description",
        description,
        "--privacy",
        privacy,
    ]
    if tags:
        cmd.extend(["--tags", *tags])
    proc = run(cmd, capture=True)
    data = json.loads(proc.stdout)
    return data


def upload_thumbnail(video_id: str, thumb: Path) -> None:
    run(
        [
            bundled_python(),
            str(WORK / "youtube_oauth_tool.py"),
            "thumbnail",
            "--video-id",
            video_id,
            "--file",
            str(thumb),
        ]
    )


def record_run(project: Path, plan: dict[str, Any], video_info: dict[str, Any], thumbnail_path: Path) -> None:
    state = load_state()
    title = plan.get("upload_title", plan.get("project_title", "Football Short"))
    state.setdefault("used_titles", []).append(title)
    state.setdefault("runs", []).append(
        {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "project": str(project),
            "title": title,
            "url": video_info.get("url", ""),
            "video_id": video_info.get("id", ""),
            "thumbnail": str(thumbnail_path),
        }
    )
    save_state(state)
    upload_record = project / "final video" / "upload records" / f"{time.strftime('%Y-%m-%d-%H%M%S')}.md"
    write_markdown(
        upload_record,
        "\n".join(
            [
                "# Upload Record",
                "",
                f"Title: {title}",
                f"Video ID: {video_info.get('id', '')}",
                f"URL: {video_info.get('url', '')}",
                f"Thumbnail: {thumbnail_path}",
                f"Project: {project}",
            ]
        ),
    )


def write_project_docs(project: Path, plan: dict[str, Any], candidates: list[NewsItem]) -> None:
    copy_text_assets(project, plan, candidates)
    save_plan_json(project, plan, candidates)


def create_project(plan: dict[str, Any]) -> Path:
    project = project_dir_for_plan(plan)
    project.mkdir(parents=True, exist_ok=True)
    make_dirs(project)
    return project


def build_pipeline() -> dict[str, Any]:
    existing_titles = scan_existing_titles()
    candidates = fetch_google_news_candidates()
    plan = select_plan(candidates, existing_titles)
    if not plan.get("folder_title"):
        number = next_video_number()
        plan["folder_title"] = f"Video {number:03d} - {safe_title_fragment(plan.get('upload_title', 'Football Short'))}"
    if not plan.get("project_title"):
        plan["project_title"] = plan.get("upload_title", "Football Short")
    if not plan.get("upload_title"):
        plan["upload_title"] = plan.get("project_title", "Football Short")
    if not plan.get("description"):
        plan["description"] = f"Latest football reaction about {plan['upload_title']}."
    if not plan.get("tags"):
        plan["tags"] = ["football", "shorts", "soccer", "news"]
    if not plan.get("script_sections"):
        plan = fallback_plan(candidates)
    return {"plan": plan, "candidates": candidates, "existing_titles": existing_titles}


def run_once(*, privacy: str = "public") -> dict[str, Any]:
    ensure_dirs()
    load_env_files()
    pipeline = build_pipeline()
    plan = pipeline["plan"]
    candidates = pipeline["candidates"]

    project = create_project(plan)
    write_project_docs(project, plan, candidates)

    voice_id = env(VOICE_ID_ENV)
    generate_voiceover(project, voice_id or None)
    speed_adjust_voiceover(project, ELEVENLABS_SPEED)

    portraits = gather_portraits(make_dirs(project), plan)
    insert_clip = download_insert_clip(plan, make_dirs(project))

    thumbnail = build_thumbnail_variants(project, plan, portraits)
    final_video = build_final_video(project, plan, portraits, insert_clip)

    upload_info = upload_youtube(
        final_video,
        plan["upload_title"],
        plan["description"],
        plan.get("tags", []),
        privacy=privacy,
    )
    if upload_info.get("id"):
        upload_thumbnail(upload_info["id"], thumbnail)

    record_run(project, plan, upload_info, thumbnail)
    summary = {
        "project": str(project),
        "title": plan["upload_title"],
        "final_video": str(final_video),
        "video_id": upload_info.get("id", ""),
        "url": upload_info.get("url", ""),
        "thumbnail": str(thumbnail),
    }
    (project / "00 instructions" / "automation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Football Shorts automation runner")
    parser.add_argument("--run-once", action="store_true", help="Run one full automation cycle now.")
    parser.add_argument("--dry-run", action="store_true", help="Only research and write files, do not upload.")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"], help="Upload privacy setting.")
    args = parser.parse_args()

    if not args.run_once:
        args.run_once = True

    acquire_lock()
    try:
        if args.dry_run:
            pipeline = build_pipeline()
            project = create_project(pipeline["plan"])
            write_project_docs(project, pipeline["plan"], pipeline["candidates"])
            print(json.dumps({"project": str(project), "title": pipeline["plan"].get("upload_title", "")}, indent=2))
            return
        summary = run_once(privacy=args.privacy)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    finally:
        release_lock()


if __name__ == "__main__":
    main()
