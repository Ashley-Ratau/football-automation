#!/usr/bin/env python3
"""
Generate football-channel voiceovers with ElevenLabs.

Default workflow:
  python work/generate_elevenlabs_voiceover.py --project "Video 001 - Norway Problem"

Required secret:
  ELEVENLABS_API_KEY in one of:
  - environment variables
  - .env.local in the Football Channel workspace
  - work/secrets/.env.local

Required voice:
  Pass --voice-id, or set ELEVENLABS_VOICE_ID in the same env file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SECRETS_DIR = ROOT / "work" / "secrets"
DEFAULT_ENV_FILES = [
    ROOT / ".env.local",
    SECRETS_DIR / ".env.local",
]

DEFAULT_MODEL = "eleven_v3"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_MAX_CHARS = 2500

DEFAULT_VOICE_SETTINGS = {
    "stability": 0.42,
    "similarity_boost": 0.82,
    "style": 0.18,
    "use_speaker_boost": True,
}


def load_env_files() -> None:
    for env_path in DEFAULT_ENV_FILES:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


def require_api_key() -> str:
    load_env_files()
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Missing ELEVENLABS_API_KEY. Add it to work/secrets/.env.local or pass it as an environment variable."
        )
    return api_key


def env_voice_id() -> str:
    load_env_files()
    return os.environ.get("ELEVENLABS_VOICE_ID", "").strip()


def project_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / value
    path = path.resolve()
    if not str(path).lower().startswith(str(ROOT.resolve()).lower()):
        raise RuntimeError(f"Project path must stay inside the workspace: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Project folder not found: {path}")
    return path


def narration_text(script_path: Path) -> str:
    text = script_path.read_text(encoding="utf-8")
    marker = "# Full Voiceover Script"
    if marker not in text:
        raise RuntimeError(f"Could not find `{marker}` in {script_path}")
    return text.split(marker, 1)[1].strip()


def split_narration(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
            continue
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = sentence
    if current:
        chunks.append(current)
    return chunks


def ffmpeg_exe() -> str:
    known = Path(
        r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
    )
    if known.exists():
        return str(known)
    return "ffmpeg"


def request_json(api_key: str, url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"xi-api-key": api_key}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs request failed: HTTP {exc.code}: {body}") from exc


def list_voices(api_key: str) -> None:
    data = request_json(api_key, "https://api.elevenlabs.io/v1/voices")
    voices = data.get("voices", [])
    print(json.dumps(
        [
            {
                "name": voice.get("name"),
                "voice_id": voice.get("voice_id"),
                "category": voice.get("category"),
                "labels": voice.get("labels", {}),
            }
            for voice in voices
        ],
        indent=2,
        ensure_ascii=False,
    ))


def synthesize_chunk(
    *,
    api_key: str,
    voice_id: str,
    text: str,
    output: Path,
    model_id: str,
    output_format: str,
    voice_settings: dict[str, Any],
) -> None:
    query = urllib.parse.urlencode({"output_format": output_format})
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{urllib.parse.quote(voice_id)}?{query}"
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": voice_settings,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as response:
            output.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs TTS failed: HTTP {exc.code}: {body}") from exc


def concat_mp3(chunks: list[Path], output: Path) -> None:
    list_path = output.parent / "concat_list.txt"
    list_path.write_text("\n".join(f"file '{path.as_posix()}'" for path in chunks), encoding="utf-8")
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
        str(output),
    ]
    subprocess.run(cmd, check=True)


def write_log(
    *,
    project: Path,
    out_dir: Path,
    final_path: Path,
    chunks: list[str],
    voice_id: str,
    model_id: str,
    output_format: str,
    voice_settings: dict[str, Any],
) -> None:
    log = project / "08 voiceover log.md"
    section = f"""

---

## ElevenLabs Voiceover

Status: generated

Provider:

ElevenLabs Text-to-Speech API

Model:

`{model_id}`

Voice ID:

`{voice_id}`

Output format:

`{output_format}`

Voice settings:

```json
{json.dumps(voice_settings, indent=2)}
```

Output folder:

`{out_dir.relative_to(project).as_posix()}/`

Final stitched MP3:

`{final_path.relative_to(project).as_posix()}`

Generated section files:

{chr(10).join(f"- `elevenlabs_part_{idx:02d}.mp3` ({len(chunk)} chars)" for idx, chunk in enumerate(chunks, 1))}

Clean narration text:

`{(out_dir / "voiceover_narration_clean.txt").relative_to(project).as_posix()}`

Generation script:

`work/generate_elevenlabs_voiceover.py`

Notes:

- This is the default voiceover provider going forward.
- The ElevenLabs API key is read from local environment/secrets and is not printed or saved in this log.
"""
    existing = log.read_text(encoding="utf-8") if log.exists() else "# Voiceover Log\n"
    log.write_text(existing.rstrip() + section, encoding="utf-8")


def generate(args: argparse.Namespace) -> None:
    api_key = require_api_key()
    project = project_path(args.project)
    script_path = project / args.script
    voice_id = args.voice_id or env_voice_id()
    if not voice_id:
        raise RuntimeError("Missing voice ID. Pass --voice-id or set ELEVENLABS_VOICE_ID.")

    text = narration_text(script_path)
    out_dir = project / "assets" / "voiceover" / "elevenlabs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "voiceover_narration_clean.txt").write_text(text, encoding="utf-8")

    if args.split_paragraphs:
        chunks = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    else:
        chunks = split_narration(text, args.max_chars)
    if args.dry_run:
        print(json.dumps(
            {
                "project": str(project),
                "script": str(script_path),
                "voice_id": voice_id,
                "model_id": args.model_id,
                "output_format": args.output_format,
                "chunks": len(chunks),
                "chars": [len(chunk) for chunk in chunks],
                "out_dir": str(out_dir),
            },
            indent=2,
        ))
        return

    chunk_paths: list[Path] = []
    for idx, chunk in enumerate(chunks, 1):
        output = out_dir / f"elevenlabs_part_{idx:02d}.mp3"
        print(f"Generating ElevenLabs part {idx}/{len(chunks)} ({len(chunk)} chars)")
        synthesize_chunk(
            api_key=api_key,
            voice_id=voice_id,
            text=chunk,
            output=output,
            model_id=args.model_id,
            output_format=args.output_format,
            voice_settings=DEFAULT_VOICE_SETTINGS,
        )
        chunk_paths.append(output)

    final_path = out_dir / "voiceover_elevenlabs_full.mp3"
    concat_mp3(chunk_paths, final_path)
    write_log(
        project=project,
        out_dir=out_dir,
        final_path=final_path,
        chunks=chunks,
        voice_id=voice_id,
        model_id=args.model_id,
        output_format=args.output_format,
        voice_settings=DEFAULT_VOICE_SETTINGS,
    )
    print(f"Generated {len(chunks)} parts")
    print(f"Final audio: {final_path}")


def check_env(_: argparse.Namespace) -> None:
    load_env_files()
    report = {
        "env_files_checked": [str(path) for path in DEFAULT_ENV_FILES],
        "api_key_present": bool(os.environ.get("ELEVENLABS_API_KEY")),
        "voice_id_present": bool(os.environ.get("ELEVENLABS_VOICE_ID")),
        "model_default": DEFAULT_MODEL,
        "output_format_default": DEFAULT_OUTPUT_FORMAT,
    }
    print(json.dumps(report, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate ElevenLabs voiceovers for football videos.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check-env", help="Check whether ElevenLabs env values are present.")
    p.set_defaults(func=check_env)

    p = sub.add_parser("voices", help="List available ElevenLabs voices for this account.")
    p.set_defaults(func=lambda args: list_voices(require_api_key()))

    p = sub.add_parser("generate", help="Generate and stitch a voiceover for a video project.")
    p.add_argument("--project", required=True, help="Video project folder, relative to the workspace or absolute.")
    p.add_argument("--script", default="03 script.md")
    p.add_argument("--voice-id", default=None)
    p.add_argument("--model-id", default=DEFAULT_MODEL)
    p.add_argument("--output-format", default=DEFAULT_OUTPUT_FORMAT)
    p.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    p.add_argument("--split-paragraphs", action="store_true", help="Force one audio chunk per paragraph.")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=generate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
