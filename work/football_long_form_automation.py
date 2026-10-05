#!/usr/bin/env python3
"""Config-driven long-form football video workflow for this workspace."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
SECRETS = WORK / "secrets" / ".env.local"
CONFIG_NAME = "long_form_project.json"
FFMPEG_FALLBACK = Path(
    r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages"
    r"\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
)
YOUTUBE_HELPER = WORK / "youtube_oauth_tool.py"
MAX_THUMBNAIL_BYTES = 2_097_152

DEFAULT_SETTINGS = {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "voice_speed": 1.2,
    "voice_gain_db": 10.0,
    "broll_clip_max_seconds": 5.5,
    "insert_fade_seconds": 0.8,
    "music_volume_db": -35.0,
    "audio_rate": 44100,
    "audio_channels": 2,
    "min_duration_seconds": 280,
    "max_duration_seconds": 900,
}


def load_env() -> None:
    if not SECRETS.exists():
        return
    for raw in SECRETS.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def ffmpeg_exe() -> str:
    return str(FFMPEG_FALLBACK) if FFMPEG_FALLBACK.exists() else "ffmpeg"


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+ " + subprocess.list2cmdline([str(x) for x in cmd]))
    return subprocess.run(
        [str(x) for x in cmd],
        check=True,
        text=True,
        capture_output=capture,
    )


def project_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Project must stay inside the Football Channel workspace: {path}") from exc
    return path


def rel_file(project: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project / path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-video"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_config(project: Path) -> dict[str, Any]:
    path = project / CONFIG_NAME
    if not path.exists():
        raise FileNotFoundError(f"Missing project config: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    data["settings"] = {**DEFAULT_SETTINGS, **data.get("settings", {})}
    return data


def scaffold_config(title: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "title": title,
        "output_filename": f"{slugify(title)}.mp4",
        "thumbnail": "assets/thumbnail/thumbnail_primary.png",
        "music_bed": "assets/music_bed.mp3",
        "settings": DEFAULT_SETTINGS,
        "upload": {
            "title": title,
            "description": "",
            "tags": ["football", "football analysis", "soccer"],
            "category": "17",
            "privacy": "unlisted",
        },
        "captions": {
            "enabled": False,
            "fontname": "Arial Black",
            "font_size": 72,
            "primary_color": "&H0000E6FF",
            "outline_color": "&H00000000",
            "back_color": "&H96000000",
            "outline": 8,
            "shadow": 4,
            "alignment": 2,
            "margin_l": 60,
            "margin_r": 60,
            "margin_v": 110,
            "group_size": 2,
        },
        "sound_effects": [],
        "research_checks": {
            "scoreline_verified": False,
            "match_number_verified": False,
            "records_verified": False,
            "availability_verified": False,
            "source_urls_recorded": False,
        },
        "sections": [
            {
                "type": "vo",
                "name": "hook",
                "text": "Replace this with the fact-checked opening hook.",
                "broll": [
                    {
                        "file": "assets/broll/main_match.mp4",
                        "start": 10,
                        "label": "hook_01",
                    }
                ],
            },
            {
                "type": "insert",
                "name": "insert_a",
                "file": "assets/broll/insert_a.mp4",
                "start": "00:00:30",
                "end": "00:00:52",
            },
            {
                "type": "vo",
                "name": "analysis",
                "text": "Replace this with the next fact-checked narration section.",
                "broll": [
                    {
                        "file": "assets/broll/secondary.mp4",
                        "start": 20,
                        "label": "analysis_01",
                    }
                ],
            },
        ],
    }


def create_project(args: argparse.Namespace) -> None:
    folder = args.folder or f"Videos/{slugify(args.title)}"
    project = project_path(folder)
    if project.exists() and any(project.iterdir()):
        raise RuntimeError(f"Project folder is not empty: {project}")

    for rel in [
        "assets/broll",
        "assets/vo",
        "assets/thumbnail",
        "_tmp/qc",
        "final video/capcut export",
        "final video/thumbnail",
        "final video/upload records",
        "CapCut Workflow/07 Edit Guides",
        "CapCut Workflow/08 Upload Package",
    ]:
        (project / rel).mkdir(parents=True, exist_ok=True)

    config = scaffold_config(args.title)
    write_text(project / CONFIG_NAME, json.dumps(config, indent=2))
    write_text(
        project / "01 idea brief.md",
        f"""# {args.title}

## Thesis

## Why now

## Target viewer

## Packaging direction
""",
    )
    write_text(
        project / "02 research dossier.md",
        """# Research Dossier

## Verified facts

## Source URLs

## Claims still needing verification

## Copyright-safe source options
""",
    )
    write_text(
        project / "03 script.md",
        f"""# Script

## Working Title

{args.title}

## Full Voiceover Script

Replace this text after completing the research dossier. Keep narration split into natural sections in
`long_form_project.json` so insert clips can fully replace the voiceover at clean handoff points.
""",
    )
    clip_map = project / "04 clip map.csv"
    with clip_map.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "Order",
                "Section",
                "Asset Needed",
                "Source URL",
                "Start",
                "End",
                "Priority",
                "Status",
                "Usage Notes",
            ]
        )
    write_text(
        project / "05 clip sourcing plan.md",
        """# Clip Sourcing Plan

## Main b-roll

## Secondary b-roll

## Insert A

## Insert B

## Rejected or high-risk sources
""",
    )
    write_text(project / "06 asset acquisition log.md", "# Asset Acquisition Log\n")
    write_text(
        project / "07 edit brief.md",
        """# Edit Brief

- Canvas: 1920x1080, 16:9
- Narration speed: 1.2x
- Inserts replace narration completely.
- No burned-in captions in the automated master.
- Upload unlisted first and review the YouTube copyright screen.
""",
    )
    write_text(project / "08 voiceover log.md", "# Voiceover Log\n")
    write_text(
        project / "CapCut Workflow/README.md",
        """# CapCut Workflow

The automated master is caption-free. Add captions and any final creative polish in CapCut, export to
`final video/capcut export/`, then upload unlisted for copyright review.
""",
    )
    print(json.dumps({"created": str(project), "config": str(project / CONFIG_NAME)}, indent=2))


def parse_time(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(part) for part in str(value).split(":")]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0]


def media_probe(path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [ffmpeg_exe(), "-hide_banner", "-i", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    text = proc.stderr + proc.stdout
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    duration = 0.0
    if duration_match:
        duration = (
            int(duration_match.group(1)) * 3600
            + int(duration_match.group(2)) * 60
            + float(duration_match.group(3))
        )
    size_match = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", text)
    return {
        "path": str(path),
        "duration": duration,
        "width": int(size_match.group(1)) if size_match else 0,
        "height": int(size_match.group(2)) if size_match else 0,
        "has_video": " Video:" in text,
        "has_audio": " Audio:" in text,
        "av1": bool(re.search(r"Video:\s*(?:av1|libdav1d)", text, re.I)),
    }


def collect_media(project: Path, config: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    media: dict[Path, dict[str, Any]] = {}
    for section in config.get("sections", []):
        if section.get("type") == "vo":
            values = [item.get("file") for item in section.get("broll", [])]
        else:
            values = [section.get("file")]
        for value in values:
            path = rel_file(project, value)
            if path and path.exists() and path not in media:
                media[path] = media_probe(path)
    music = rel_file(project, config.get("music_bed"))
    if music and music.exists():
        media[music] = media_probe(music)
    return media


def validation_report(project: Path, config: dict[str, Any]) -> dict[str, Any]:
    settings = config["settings"]
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    media = collect_media(project, config)

    research = config.get("research_checks", {})
    missing_research = [key for key, value in research.items() if not value]
    if missing_research:
        errors.append("Research checklist is incomplete: " + ", ".join(missing_research))

    sections = config.get("sections", [])
    if not sections:
        errors.append("No sections are configured.")
    if sum(1 for section in sections if section.get("type") == "insert") > 6:
        warnings.append("More than six inserts are configured; long-form videos should remain narration-led.")
    section_names = {(section.get("name") or f"section_{index:02d}") for index, section in enumerate(sections, 1)}

    for index, section in enumerate(sections, 1):
        kind = section.get("type")
        name = section.get("name") or f"section_{index:02d}"
        if kind == "vo":
            if not str(section.get("text", "")).strip():
                errors.append(f"{name}: voiceover text is empty.")
            broll = section.get("broll", [])
            if not broll:
                errors.append(f"{name}: no b-roll is configured.")
            for item in broll:
                path = rel_file(project, item.get("file"))
                if not path or not path.exists():
                    errors.append(f"{name}: missing b-roll file {item.get('file')!r}.")
                    continue
                probe = media[path]
                offset = parse_time(item.get("start", 0))
                requested_duration = min(
                    float(item.get("duration", settings["broll_clip_max_seconds"])),
                    float(settings["broll_clip_max_seconds"]),
                )
                max_safe = probe["duration"] - requested_duration - 1
                if offset > max_safe:
                    errors.append(
                        f"{name}: b-roll offset {offset:.2f}s exceeds safe maximum "
                        f"{max_safe:.2f}s for {path.name}."
                    )
                if probe["av1"]:
                    errors.append(f"{name}: AV1 source rejected for reliability: {path.name}.")
        elif kind == "insert":
            path = rel_file(project, section.get("file"))
            if not path or not path.exists():
                errors.append(f"{name}: missing insert file {section.get('file')!r}.")
                continue
            start = parse_time(section.get("start", 0))
            end = parse_time(section.get("end", 0))
            if end <= start:
                errors.append(f"{name}: insert end must be after start.")
            if end > media[path]["duration"]:
                errors.append(
                    f"{name}: insert ends at {end:.2f}s but source is only "
                    f"{media[path]['duration']:.2f}s."
                )
            if not media[path]["has_audio"]:
                errors.append(f"{name}: insert must have its own audio: {path.name}.")
            if media[path]["av1"]:
                errors.append(f"{name}: AV1 source rejected for reliability: {path.name}.")
        else:
            errors.append(f"{name}: type must be 'vo' or 'insert'.")

    for cue in config.get("sound_effects", []):
        cue_name = str(cue.get("name") or "unnamed_sfx")
        cue_file = cue.get("file")
        cue_prompt = str(cue.get("prompt") or "").strip()
        if not cue_file and not cue_prompt:
            errors.append(f"sound effect {cue_name}: provide either file or prompt.")
        if cue_file:
            cue_path = rel_file(project, str(cue_file))
            if not cue_path or not cue_path.exists():
                errors.append(f"sound effect {cue_name}: file does not exist: {cue_file!r}.")
        duration_seconds = float(cue.get("duration_seconds", 0) or 0)
        if not 0.5 <= duration_seconds <= 30:
            errors.append(f"sound effect {cue_name}: duration_seconds must be between 0.5 and 30.")
        anchor = cue.get("anchor_section")
        if anchor and anchor not in section_names:
            errors.append(f"sound effect {cue_name}: unknown anchor_section {anchor!r}.")

    for path, probe in media.items():
        checks.append({"file": str(path.relative_to(project)), **{k: v for k, v in probe.items() if k != "path"}})

    thumbnail = rel_file(project, config.get("thumbnail"))
    if thumbnail and thumbnail.exists():
        try:
            with Image.open(thumbnail) as image:
                ratio = image.width / image.height
                if abs(ratio - (16 / 9)) > 0.03:
                    warnings.append(
                        f"Thumbnail is {image.width}x{image.height}; use standard YouTube 16:9."
                    )
        except OSError:
            errors.append(f"Thumbnail cannot be opened: {thumbnail}")
    else:
        warnings.append("Thumbnail is not ready yet.")

    return {
        "project": str(project),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "media": checks,
    }


def validate_project(args: argparse.Namespace) -> None:
    project = project_path(args.project)
    report = validation_report(project, load_config(project))
    out = project / "_tmp" / "preflight_report.json"
    write_text(out, json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not report["valid"]:
        raise SystemExit(1)


def generate_voiceover(text: str, output: Path, model_id: str) -> None:
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from work/secrets/.env.local.")
    voice = "Orus"
    payload = {
        "model": model_id,
        "input": (
            "Read the following narration exactly as written. Use a confident, natural "
            "documentary delivery with clear pacing. Do not add an introduction, filler "
            "sounds, commentary, or any words not present in the narration.\n\n"
            f"{text}"
        ),
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
            "Api-Revision": "2026-05-20",
        },
        method="POST",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini TTS failed: HTTP {exc.code}: {body}") from exc

    audio: dict[str, Any] | None = None
    for step in result.get("steps", []):
        for item in step.get("content", []):
            if item.get("type") == "audio" and item.get("data"):
                audio = item
                break
        if audio:
            break
    if not audio:
        raise RuntimeError("Gemini TTS completed without an audio payload.")
    if str(audio.get("mime_type", "")).split(";", 1)[0].strip().lower() != "audio/l16":
        raise RuntimeError(f"Unsupported Gemini TTS audio type: {audio.get('mime_type')!r}.")

    pcm = base64.b64decode(audio["data"])
    channels = int(audio.get("channels", 1))
    sample_rate = int(audio.get("sample_rate", 24000))
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm)


def generate_sound_effect(
    text: str,
    output: Path,
    *,
    duration_seconds: float | None = None,
    prompt_influence: float = 0.45,
    model_id: str = "eleven_text_to_sound_v2",
) -> None:
    load_env()
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ElevenLabs API key is missing from work/secrets/.env.local.")
    query = urllib.parse.urlencode({"output_format": "mp3_44100_128"})
    url = f"https://api.elevenlabs.io/v1/sound-generation?{query}"
    payload: dict[str, Any] = {
        "text": text,
        "model_id": model_id,
        "prompt_influence": prompt_influence,
    }
    if duration_seconds is not None:
        payload["duration_seconds"] = duration_seconds
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
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(req, timeout=240) as response:
            output.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs sound effect generation failed: HTTP {exc.code}: {body}") from exc


def process_voice(raw: Path, output: Path, settings: dict[str, Any]) -> None:
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(raw),
            "-filter:a",
            (
                f"atempo={settings['voice_speed']},"
                f"volume={settings['voice_gain_db']}dB,"
                "acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120,"
                "alimiter=limit=0.97"
            ),
            "-ar",
            str(settings["audio_rate"]),
            "-ac",
            str(settings["audio_channels"]),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output),
        ]
    )


def add_pause_to_av(
    video_in: Path,
    audio_in: Path,
    video_out: Path,
    audio_out: Path,
    pause_seconds: float,
    settings: dict[str, Any],
) -> float:
    pause = max(0.0, float(pause_seconds))
    if pause <= 0:
        shutil.copy2(video_in, video_out)
        shutil.copy2(audio_in, audio_out)
        return media_probe(audio_out)["duration"]

    run(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(video_in),
            "-vf",
            f"tpad=stop_mode=clone:stop_duration={pause:.3f}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            str(video_out),
        ]
    )
    total = media_probe(audio_in)["duration"] + pause
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(audio_in),
            "-af",
            f"apad=whole_dur={total:.3f}",
            "-t",
            f"{total:.3f}",
            "-ar",
            str(settings["audio_rate"]),
            "-ac",
            str(settings["audio_channels"]),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(audio_out),
        ]
    )
    # ADTS AAC duration probes are bitrate estimates and can under-report padded
    # silence. FFmpeg is explicitly constrained to the calculated total above.
    return total


def render_broll_visual(
    project: Path,
    section: dict[str, Any],
    duration: float,
    output: Path,
    settings: dict[str, Any],
) -> None:
    tmp = output.parent / f"{output.stem}_clips"
    tmp.mkdir(parents=True, exist_ok=True)
    items = section["broll"]
    max_clip = float(settings["broll_clip_max_seconds"])
    clips: list[Path] = []
    remaining = duration + 0.5

    index = 0
    while remaining > 0.001:
        item = items[index % len(items)]
        source = rel_file(project, item["file"])
        requested_duration = max(0.25, float(item.get("duration", max_clip)))
        clip_duration = min(max_clip, requested_duration, remaining)
        clip = tmp / f"clip_{index + 1:03d}.mp4"
        vf = (
            f"scale={settings['width']}:{settings['height']}:"
            "force_original_aspect_ratio=increase,"
            f"crop={settings['width']}:{settings['height']},fps={settings['fps']}"
        )
        run(
            [
                ffmpeg_exe(),
                "-y",
                "-ss",
                str(parse_time(item.get("start", 0))),
                "-t",
                f"{clip_duration:.3f}",
                "-i",
                str(source),
                "-an",
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                str(clip),
            ]
        )
        clips.append(clip)
        remaining -= clip_duration
        index += 1

    concat = tmp / "concat.txt"
    write_text(concat, "\n".join(f"file '{path.as_posix()}'" for path in clips))
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(output),
        ]
    )


def render_vo_section(
    project: Path,
    section: dict[str, Any],
    index: int,
    output: Path,
    settings: dict[str, Any],
    model_id: str,
    skip_tts: bool,
) -> float:
    name = section.get("name") or f"section_{index:02d}"
    raw = project / "assets" / "vo" / f"{index:02d}_{name}_raw.wav"
    processed = project / "_tmp" / f"{index:02d}_{name}_voice.aac"
    if not raw.exists():
        if skip_tts:
            raise FileNotFoundError(f"Missing voiceover while --skip-tts is active: {raw}")
        generate_voiceover(section["text"], raw, model_id)
    process_voice(raw, processed, settings)
    voice_duration = media_probe(processed)["duration"]
    visual = project / "_tmp" / f"{index:02d}_{name}_visual.mp4"
    render_broll_visual(project, section, voice_duration, visual, settings)
    pause_after = max(0.0, float(section.get("pause_after_seconds", 0.0) or 0.0))
    final_visual = visual
    final_audio = processed
    duration = voice_duration
    if pause_after > 0:
        padded_visual = project / "_tmp" / f"{index:02d}_{name}_visual_padded.mp4"
        padded_audio = project / "_tmp" / f"{index:02d}_{name}_voice_padded.aac"
        duration = add_pause_to_av(
            visual,
            processed,
            padded_visual,
            padded_audio,
            pause_after,
            settings,
        )
        final_visual = padded_visual
        final_audio = padded_audio
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(final_visual),
            "-i",
            str(final_audio),
            "-t",
            f"{duration:.3f}",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(settings["audio_rate"]),
            "-ac",
            str(settings["audio_channels"]),
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    check = project / "assets" / "vo" / f"{index:02d}_{name}_check2s.wav"
    run([ffmpeg_exe(), "-y", "-i", str(raw), "-t", "2", "-c:a", "copy", str(check)])
    return duration


def render_insert_section(
    project: Path,
    section: dict[str, Any],
    output: Path,
    settings: dict[str, Any],
) -> float:
    source = rel_file(project, section["file"])
    start = parse_time(section["start"])
    end = parse_time(section["end"])
    duration = end - start
    fade = min(float(settings["insert_fade_seconds"]), duration / 3)
    fade_start = max(0.0, duration - fade)
    vf = (
        f"scale={settings['width']}:{settings['height']}:"
        "force_original_aspect_ratio=increase,"
        f"crop={settings['width']}:{settings['height']},fps={settings['fps']},"
        f"fade=t=out:st={fade_start:.3f}:d={fade:.3f}"
    )
    af = (
        f"afade=t=out:st={fade_start:.3f}:d={fade:.3f},"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(source),
            "-vf",
            vf,
            "-af",
            af,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(settings["audio_rate"]),
            "-ac",
            str(settings["audio_channels"]),
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return duration


def mix_music(source: Path, music: Path, output: Path, settings: dict[str, Any]) -> None:
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(source),
            "-stream_loop",
            "-1",
            "-i",
            str(music),
            "-filter_complex",
            (
                f"[1:a]volume={settings['music_volume_db']}dB[music];"
                "[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]"
            ),
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(settings["audio_rate"]),
            "-ac",
            str(settings["audio_channels"]),
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


def timeline_starts(timeline: list[dict[str, Any]]) -> dict[str, float]:
    starts: dict[str, float] = {}
    cursor = 0.0
    for item in timeline:
        starts[item["name"]] = cursor
        cursor += float(item["duration"])
    return starts


def ensure_sound_effects(project: Path, config: dict[str, Any], timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    starts = timeline_starts(timeline)
    cues: list[dict[str, Any]] = []
    for raw_cue in config.get("sound_effects", []):
        cue = dict(raw_cue)
        if cue.get("file"):
            path = rel_file(project, str(cue["file"]))
            if path is None:
                raise RuntimeError(f"Invalid sound effect file for cue {cue['name']}.")
        else:
            path = project / "assets" / "sfx" / f"{cue['name']}.mp3"
            if not path.exists():
                generate_sound_effect(
                    cue["prompt"],
                    path,
                    duration_seconds=float(cue.get("duration_seconds")) if cue.get("duration_seconds") is not None else None,
                    prompt_influence=float(cue.get("prompt_influence", 0.45)),
                    model_id=str(cue.get("model_id", "eleven_text_to_sound_v2")),
                )
        start_seconds = float(cue.get("start_seconds", cue.get("offset_seconds", 0.0)) or 0.0)
        anchor = cue.get("anchor_section")
        if anchor:
            start_seconds += starts[anchor]
        cue["path"] = path
        cue["start_seconds"] = max(0.0, start_seconds)
        cue["probe"] = media_probe(path)
        cues.append(cue)
    return cues


def mix_sound_effects(source: Path, cues: list[dict[str, Any]], output: Path, settings: dict[str, Any]) -> None:
    if not cues:
        shutil.copy2(source, output)
        return
    cmd: list[str] = [ffmpeg_exe(), "-y", "-i", str(source)]
    for cue in cues:
        cmd.extend(["-i", str(cue["path"])])
    filter_parts: list[str] = []
    mix_inputs = ["[0:a]"]
    for index, cue in enumerate(cues, 1):
        delay_ms = int(round(float(cue["start_seconds"]) * 1000))
        volume_db = float(cue.get("volume_db", -16.0))
        fade_out = float(cue.get("fade_out_seconds", 0.0) or 0.0)
        cue_duration = float(cue["probe"]["duration"])
        label = f"sfx{index}"
        chain = f"[{index}:a]volume={volume_db}dB"
        if fade_out > 0 and cue_duration > fade_out:
            chain += f",afade=t=out:st={cue_duration - fade_out:.3f}:d={fade_out:.3f}"
        chain += f",adelay={delay_ms}|{delay_ms}[{label}]"
        filter_parts.append(chain)
        mix_inputs.append(f"[{label}]")
    filter_parts.append(
        "".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0[a]"
    )
    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(settings["audio_rate"]),
            "-ac",
            str(settings["audio_channels"]),
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run(cmd)


def ass_time(seconds: float) -> str:
    total = max(0.0, seconds)
    hours = int(total // 3600)
    minutes = int((total % 3600) // 60)
    secs = total % 60
    centis = int(round((secs - int(secs)) * 100))
    whole = int(secs)
    if centis == 100:
        whole += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{whole:02d}.{centis:02d}"


def caption_groups_from_audio(audio_path: Path, fallback_text: str, duration: float, group_size: int) -> list[tuple[float, float, str]]:
    words_from_text = re.findall(r"[A-Za-z0-9']+", fallback_text.upper())
    if not words_from_text:
        return []
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio_path), beam_size=5, language="en", word_timestamps=True, vad_filter=False)
        timed_words: list[tuple[float, float, str]] = []
        for seg in segments:
            for word in getattr(seg, "words", []) or []:
                token = re.sub(r"[^A-Z0-9']+", "", str(word.word).upper())
                if token:
                    timed_words.append((float(word.start), float(word.end), token))
        if timed_words:
            groups: list[tuple[float, float, str]] = []
            total_script_words = len(words_from_text)
            total_timed_words = len(timed_words)
            for index in range(0, total_script_words, group_size):
                script_chunk = words_from_text[index : index + group_size]
                timed_start_idx = min(total_timed_words - 1, max(0, round(index * total_timed_words / total_script_words)))
                timed_end_idx = min(
                    total_timed_words - 1,
                    max(
                        timed_start_idx,
                        round((min(total_script_words, index + group_size) * total_timed_words) / total_script_words) - 1,
                    ),
                )
                groups.append(
                    (
                        timed_words[timed_start_idx][0],
                        timed_words[timed_end_idx][1],
                        " ".join(script_chunk),
                    )
                )
            return groups
    except Exception:
        pass

    groups: list[tuple[float, float, str]] = []
    chunk_words = [" ".join(words_from_text[i : i + group_size]) for i in range(0, len(words_from_text), group_size)]
    if not chunk_words:
        return []
    slice_duration = duration / len(chunk_words)
    cursor = 0.0
    for chunk in chunk_words:
        start = cursor
        end = min(duration, cursor + slice_duration)
        groups.append((start, end, chunk))
        cursor = end
    return groups


def write_ass_captions(project: Path, config: dict[str, Any], timeline: list[dict[str, Any]]) -> Path:
    captions = config.get("captions", {})
    style = {
        "fontname": captions.get("fontname", "Arial Black"),
        "font_size": int(captions.get("font_size", 72)),
        "primary_color": captions.get("primary_color", "&H0000E6FF"),
        "outline_color": captions.get("outline_color", "&H00000000"),
        "back_color": captions.get("back_color", "&H96000000"),
        "outline": int(captions.get("outline", 8)),
        "shadow": int(captions.get("shadow", 4)),
        "alignment": int(captions.get("alignment", 2)),
        "margin_l": int(captions.get("margin_l", 60)),
        "margin_r": int(captions.get("margin_r", 60)),
        "margin_v": int(captions.get("margin_v", 110)),
        "group_size": int(captions.get("group_size", 2)),
    }
    events: list[str] = []
    cursor = 0.0
    for index, section in enumerate(config["sections"], 1):
        section_name = section.get("name") or f"section_{index:02d}"
        timeline_item = timeline[index - 1]
        if section["type"] != "vo":
            cursor += float(timeline_item["duration"])
            continue
        pause_after = float(section.get("pause_after_seconds", 0.0) or 0.0)
        voice_duration = max(0.0, float(timeline_item["duration"]) - pause_after)
        audio_path = project / "_tmp" / f"{index:02d}_{section_name}_voice.aac"
        groups = caption_groups_from_audio(audio_path, section["text"], voice_duration, style["group_size"])
        for start, end, text in groups:
            if end <= start:
                continue
            event = (
                "Dialogue: 0,"
                f"{ass_time(cursor + start)},{ass_time(cursor + end)},Hormozi,,0,0,0,,"
                "{\\fad(25,25)\\t(0,70,\\fscx112\\fscy112)\\t(70,150,\\fscx100\\fscy100)}"
                + text.replace("\n", " ").upper()
            )
            events.append(event)
        cursor += float(timeline_item["duration"])

    ass_path = project / "_tmp" / "long_form_captions.ass"
    content = "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1920",
            "PlayResY: 1080",
            "[V4+ Styles]",
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
            (
                "Style: Hormozi,"
                f"{style['fontname']},{style['font_size']},{style['primary_color']},&H000000FF,"
                f"{style['outline_color']},{style['back_color']},-1,0,0,0,100,100,0,0,1,"
                f"{style['outline']},{style['shadow']},{style['alignment']},{style['margin_l']},{style['margin_r']},{style['margin_v']},1"
            ),
            "[Events]",
            "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
            *events,
            "",
        ]
    )
    write_text(ass_path, content)
    return ass_path


def burn_ass_captions(source: Path, ass_path: Path, output: Path) -> None:
    ass_filter = str(ass_path).replace("\\", "/").replace(":", "\\:")
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(source),
            "-vf",
            f"ass='{ass_filter}'",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


def extract_qc_frames(project: Path, final_video: Path, timeline: list[dict[str, Any]]) -> None:
    qc_dir = project / "_tmp" / "qc"
    qc_dir.mkdir(parents=True, exist_ok=True)
    cursor = 0.0
    for index, item in enumerate(timeline, 1):
        timestamp = cursor + min(item["duration"] / 2, max(1.0, item["duration"] - 0.5))
        name = re.sub(r"[^a-z0-9]+", "_", item["name"].lower()).strip("_")
        output = qc_dir / f"qc_{index:02d}_{name}.jpg"
        run(
            [
                ffmpeg_exe(),
                "-y",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(final_video),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output),
            ]
        )
        cursor += item["duration"]


def build_project(args: argparse.Namespace) -> None:
    project = project_path(args.project)
    config = load_config(project)
    report = validation_report(project, config)
    if not report["valid"]:
        print(json.dumps(report, indent=2))
        raise RuntimeError("Preflight failed. Fix the reported errors before rendering.")

    tmp = project / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    final_dir = project / "final video"
    final_dir.mkdir(parents=True, exist_ok=True)
    settings = config["settings"]
    model_id = args.model_id
    timeline: list[dict[str, Any]] = []
    rendered: list[Path] = []

    for index, section in enumerate(config["sections"], 1):
        name = section.get("name") or f"section_{index:02d}"
        output = tmp / f"segment_{index:02d}_{name}.mp4"
        if section["type"] == "vo":
            duration = render_vo_section(
                project,
                section,
                index,
                output,
                settings,
                model_id,
                args.skip_tts,
            )
        else:
            duration = render_insert_section(project, section, output, settings)
        rendered.append(output)
        timeline.append({"index": index, "name": name, "type": section["type"], "duration": duration})

    concat = tmp / "segments_concat.txt"
    write_text(concat, "\n".join(f"file '{path.as_posix()}'" for path in rendered))
    assembled = tmp / "assembled_no_music.mp4"
    run(
        [
            ffmpeg_exe(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(assembled),
        ]
    )

    final_video = final_dir / config.get("output_filename", "long-form-video.mp4")
    working_master = assembled
    music = rel_file(project, config.get("music_bed"))
    if music and music.exists():
        with_music = tmp / "assembled_with_music.mp4"
        mix_music(assembled, music, with_music, settings)
        working_master = with_music
    cues = ensure_sound_effects(project, config, timeline)
    if cues:
        with_sfx = tmp / "assembled_with_sfx.mp4"
        mix_sound_effects(working_master, cues, with_sfx, settings)
        working_master = with_sfx
    captions = config.get("captions", {})
    captions_enabled = bool(captions.get("enabled"))
    ass_path: Path | None = None
    if captions_enabled:
        ass_path = write_ass_captions(project, config, timeline)
        with_captions = tmp / "assembled_with_captions.mp4"
        burn_ass_captions(working_master, ass_path, with_captions)
        working_master = with_captions
    shutil.copy2(working_master, final_video)

    probe = media_probe(final_video)
    specs_ok = (
        probe["has_video"]
        and probe["has_audio"]
        and probe["width"] == int(settings["width"])
        and probe["height"] == int(settings["height"])
        and float(settings["min_duration_seconds"])
        <= probe["duration"]
        <= float(settings["max_duration_seconds"])
    )
    extract_qc_frames(project, final_video, timeline)
    build_report = {
        "project": str(project),
        "final_video": str(final_video),
        "specs_ok": specs_ok,
        "probe": probe,
        "timeline": timeline,
        "sound_effects": [
            {
                "name": cue["name"],
                "start_seconds": cue["start_seconds"],
                "duration": cue["probe"]["duration"],
                "path": str(cue["path"]),
            }
            for cue in cues
        ],
        "captions_enabled": captions_enabled,
        "captions_ass": str(ass_path) if ass_path else "",
        "qc_dir": str(project / "_tmp" / "qc"),
        "voice_model": model_id,
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    write_text(final_dir / "build_report.json", json.dumps(build_report, indent=2))
    print(json.dumps(build_report, indent=2))
    if not specs_ok:
        raise RuntimeError("Render completed, but final specification checks failed.")


def prepare_thumbnail(project: Path, config: dict[str, Any]) -> Path:
    source = rel_file(project, config.get("thumbnail"))
    if not source or not source.exists():
        raise FileNotFoundError("Configured thumbnail does not exist.")
    output = project / "final video" / "thumbnail" / f"{source.stem}.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        for quality in [90, 82, 75, 68, 60]:
            rgb.save(output, "JPEG", quality=quality, optimize=True)
            if output.stat().st_size < MAX_THUMBNAIL_BYTES:
                return output
    raise RuntimeError("Could not compress thumbnail below YouTube's 2MB limit.")


def prepare_upload(args: argparse.Namespace) -> None:
    project = project_path(args.project)
    config = load_config(project)
    final_video = project / "final video" / config.get("output_filename", "long-form-video.mp4")
    if not final_video.exists():
        raise FileNotFoundError(f"Final video not found: {final_video}")
    thumbnail = prepare_thumbnail(project, config)
    upload = config.get("upload", {})
    privacy = upload.get("privacy", "unlisted")
    if privacy not in {"private", "unlisted"}:
        raise RuntimeError("Automated uploads may only use private or unlisted privacy.")
    command = [
        sys.executable,
        str(YOUTUBE_HELPER),
        "upload",
        "--file",
        str(final_video),
        "--title",
        upload.get("title") or config["title"],
        "--description",
        upload.get("description", ""),
        "--privacy",
        privacy,
        "--category",
        upload.get("category", "17"),
    ]
    tags = upload.get("tags", [])
    if tags:
        command.extend(["--tags", *tags])
    package = {
        "video": str(final_video),
        "thumbnail_jpeg": str(thumbnail),
        "thumbnail_bytes": thumbnail.stat().st_size,
        "upload_command": command,
        "privacy": privacy,
        "next_steps": [
            "Run the upload only after reviewing every QC frame and VO check file.",
            "Set the returned video ID thumbnail with youtube_oauth_tool.py thumbnail.",
            "Review the YouTube copyright screen before changing privacy to public.",
        ],
    }
    write_text(
        project / "CapCut Workflow" / "08 Upload Package" / "automation_upload_package.json",
        json.dumps(package, indent=2),
    )
    print(json.dumps(package, indent=2))


def upload_project(args: argparse.Namespace) -> None:
    if not args.confirm_upload:
        raise RuntimeError("Upload requires --confirm-upload.")
    project = project_path(args.project)
    config = load_config(project)
    final_video = project / "final video" / config.get("output_filename", "long-form-video.mp4")
    thumbnail = prepare_thumbnail(project, config)
    upload = config.get("upload", {})
    privacy = upload.get("privacy", "unlisted")
    if privacy not in {"private", "unlisted"}:
        raise RuntimeError("Automated uploads may only use private or unlisted privacy.")
    command = [
        sys.executable,
        str(YOUTUBE_HELPER),
        "upload",
        "--file",
        str(final_video),
        "--title",
        upload.get("title") or config["title"],
        "--description",
        upload.get("description", ""),
        "--privacy",
        privacy,
        "--category",
        upload.get("category", "17"),
    ]
    if upload.get("tags"):
        command.extend(["--tags", *upload["tags"]])
    proc = run(command, capture=True)
    print(proc.stdout)
    matches = re.findall(r'"id":\s*"([^"]+)"', proc.stdout)
    if not matches:
        raise RuntimeError("Upload completed without a parseable video ID.")
    video_id = matches[-1]
    run(
        [
            sys.executable,
            str(YOUTUBE_HELPER),
            "thumbnail",
            "--video-id",
            video_id,
            "--file",
            str(thumbnail),
        ]
    )
    record = project / "final video" / "upload records" / f"{time.strftime('%Y-%m-%d-%H%M%S')}.md"
    write_text(
        record,
        f"""# YouTube Upload

- Video ID: `{video_id}`
- URL: https://www.youtube.com/watch?v={video_id}
- Privacy: {privacy}
- Thumbnail: `{thumbnail}`

Review the copyright screen before publishing or changing visibility.
""",
    )


def doctor(_: argparse.Namespace) -> None:
    load_env()
    checks = {
        "workspace": str(ROOT),
        "python": sys.executable,
        "ffmpeg": ffmpeg_exe(),
        "ffmpeg_available": FFMPEG_FALLBACK.exists() or shutil.which("ffmpeg") is not None,
        "yt_dlp_available": shutil.which("yt-dlp") is not None,
        "gemini_api_key_present": bool(os.environ.get("GEMINI_API_KEY")),
        "gemini_tts_model": "gemini-3.1-flash-tts-preview",
        "gemini_tts_voice": "Orus",
        "youtube_helper": YOUTUBE_HELPER.exists(),
        "youtube_client": (WORK / "secrets" / "youtube_oauth_client.json").exists(),
        "youtube_token": (WORK / "secrets" / "youtube_token_youtube_only.json").exists(),
        "drive_token": (WORK / "secrets" / "youtube_token_drive_only.json").exists(),
    }
    checks["ready"] = all(
        checks[key]
        for key in [
            "ffmpeg_available",
            "yt_dlp_available",
            "gemini_api_key_present",
            "youtube_helper",
            "youtube_client",
            "youtube_token",
        ]
    )
    print(json.dumps(checks, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Football Channel long-form automation.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("doctor", help="Check local long-form prerequisites.")
    p.set_defaults(func=doctor)

    p = sub.add_parser("create", help="Create a new long-form project scaffold.")
    p.add_argument("--title", required=True)
    p.add_argument("--folder", default=None, help="Workspace-relative destination folder.")
    p.set_defaults(func=create_project)

    p = sub.add_parser("validate", help="Validate research gates, media, offsets, and thumbnail.")
    p.add_argument("--project", required=True)
    p.set_defaults(func=validate_project)

    p = sub.add_parser("build", help="Generate section VO, render, verify, and extract QC frames.")
    p.add_argument("--project", required=True)
    p.add_argument("--model-id", default="gemini-3.1-flash-tts-preview")
    p.add_argument("--skip-tts", action="store_true")
    p.set_defaults(func=build_project)

    p = sub.add_parser("prepare-upload", help="Compress thumbnail and write an unlisted upload package.")
    p.add_argument("--project", required=True)
    p.set_defaults(func=prepare_upload)

    p = sub.add_parser("upload", help="Upload the verified final as private/unlisted and set its thumbnail.")
    p.add_argument("--project", required=True)
    p.add_argument("--confirm-upload", action="store_true")
    p.set_defaults(func=upload_project)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
