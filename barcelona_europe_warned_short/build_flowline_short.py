# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 FlowLine Studio contributors

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import requests


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "assets" / "raw"
VO = ROOT / "assets" / "vo"
MUSIC = ROOT / "assets" / "music"
EDIT = ROOT / "edit"
SHOTS = EDIT / "shots"
FINAL = ROOT / "final video"
SCRIPT = (ROOT / "script.txt").read_text(encoding="utf-8").strip()
VOICE_RAW = VO / "barcelona_voiceover.mp3"
VOICE = VO / "barcelona_voiceover_normalized.m4a"
ALIGNMENT = VO / "barcelona_voiceover_alignment.json"
CAPTIONS = EDIT / "captions.ass"
PLAN = EDIT / "flowline_plan.json"
PREVIEW = FINAL / "barcelona_europe_warned_preview.mp4"
PROJECT = ROOT / "flowline_project"
FLOWLINE = Path(r"C:\Users\Wendy\Documents\FlowLineStudio")
CLI = FLOWLINE / "engine" / "target" / "debug" / "concat-cli.exe"
ENV_FILE = Path(r"C:\Users\Wendy\Documents\Football Channel\work\secrets\.env.local")
W, H, FPS = 1080, 1920, 30

SOURCE_MOMENTS = [
    ("barcelona_racing_7_2.mp4", 5.0, "Raphinha flare entrance"),
    ("barcelona_racing_7_2.mp4", 21.0, "Racing pressure"),
    ("barcelona_racing_7_2.mp4", 42.0, "Racing celebration"),
    ("barcelona_feyenoord_5_1.mp4", 5.0, "European opening"),
    ("barcelona_feyenoord_5_1.mp4", 24.0, "Feyenoord attack"),
    ("barcelona_racing_7_2.mp4", 61.0, "Raphinha sequence"),
    ("barcelona_feyenoord_5_1.mp4", 43.0, "Champions League goal"),
    ("barcelona_racing_7_2.mp4", 82.0, "Barcelona close-up"),
    ("barcelona_racing_7_2.mp4", 101.0, "Racing second-half attack"),
    ("barcelona_feyenoord_5_1.mp4", 63.0, "European transition"),
    ("barcelona_racing_7_2.mp4", 121.0, "Barcelona movement"),
    ("barcelona_feyenoord_5_1.mp4", 82.0, "Goal celebration"),
    ("barcelona_racing_7_2.mp4", 141.0, "Late Racing goal"),
    ("barcelona_feyenoord_5_1.mp4", 103.0, "European final attack"),
    ("barcelona_racing_7_2.mp4", 161.0, "Winning celebration"),
]


def run(command: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    print(">", " ".join(map(str, command))[:240], flush=True)
    return subprocess.run(command, check=True, text=True, capture_output=capture)


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def duration(path: Path) -> float:
    result = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture=True)
    return float(result.stdout.strip())


def generate_voice() -> None:
    if not VOICE_RAW.exists() or not ALIGNMENT.exists():
        load_env()
        key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not key:
            raise RuntimeError("ELEVENLABS_API_KEY is missing")
        voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json={
                "text": SCRIPT,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.52,
                    "similarity_boost": 0.82,
                    "style": 0.28,
                    "use_speaker_boost": True,
                    "speed": 1.06,
                },
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        VOICE_RAW.write_bytes(base64.b64decode(data["audio_base64"]))
        ALIGNMENT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if not VOICE.exists():
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(VOICE_RAW),
            "-af", "loudnorm=I=-16:LRA=7:TP=-1.5", "-ar", "44100", "-ac", "2",
            "-c:a", "aac", "-b:a", "192k", str(VOICE),
        ])


def words() -> list[dict]:
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    alignment = data.get("normalized_alignment") or data["alignment"]
    output: list[dict] = []
    chars: list[str] = []
    starts: list[float] = []
    ends: list[float] = []
    for char, start, end in zip(
        alignment["characters"],
        alignment["character_start_times_seconds"],
        alignment["character_end_times_seconds"],
    ):
        if re.match(r"[A-Za-z0-9'’-]", char):
            chars.append(char)
            starts.append(start)
            ends.append(end)
        elif chars:
            output.append({"text": "".join(chars), "start": starts[0], "end": ends[-1]})
            chars, starts, ends = [], [], []
    if chars:
        output.append({"text": "".join(chars), "start": starts[0], "end": ends[-1]})
    return output


def ass_time(seconds: float) -> str:
    centis = round(seconds * 100)
    hours, centis = divmod(centis, 360000)
    minutes, centis = divmod(centis, 6000)
    secs, centis = divmod(centis, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def caption_groups(items: list[dict]) -> list[dict]:
    groups = []
    for index in range(0, len(items), 2):
        pair = items[index:index + 2]
        groups.append({
            "text": " ".join(word["text"] for word in pair).upper(),
            "start": max(0.0, pair[0]["start"] - 0.03),
            "duration": pair[-1]["end"] - pair[0]["start"] + 0.11,
        })
    return groups


def write_captions(groups: list[dict]) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Arial,50,&H00FFFFFF,&H0000FFFF,&H00000000,&H70000000,1,0,0,0,100,100,-1,0,1,7,0,5,55,55,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for group in groups:
        end = group["start"] + group["duration"]
        lines.append(
            f"Dialogue: 0,{ass_time(group['start'])},{ass_time(end)},Main,,0,0,0,,{group['text']}"
        )
    CAPTIONS.write_text("\n".join(lines), encoding="utf-8")


def build_shots(total: float) -> list[dict]:
    shots: list[dict] = []
    cursor = 0.0
    index = 0
    while cursor < total - 0.01:
        source_name, source_start, label = SOURCE_MOMENTS[index % len(SOURCE_MOMENTS)]
        length = min(3.0 if index else 2.2, total - cursor)
        output = SHOTS / f"shot_{index:02d}.mp4"
        # Rebuild deterministically so framing changes are reflected in both
        # the FlowLine timeline and exported preview.
        if True:
            run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", str(source_start), "-i", str(RAW / source_name), "-t", f"{length:.3f}",
                "-filter_complex",
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,format=yuv420p,fps=30[v]",
                "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                str(output),
            ])
        shots.append({
            "file": str(output), "start": round(cursor, 3), "duration": round(length, 3),
            "source": str(RAW / source_name), "sourceStart": source_start, "label": label,
        })
        cursor += length
        index += 1
    return shots


def build_music(total: float) -> Path:
    output = MUSIC / "pressure_bed.m4a"
    if not output.exists():
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
            f"aevalsrc=0.028*sin(2*PI*52*t)+0.014*sin(2*PI*104*t)+0.009*sin(2*PI*156*t):s=44100:d={total}",
            "-af", f"afade=t=in:st=0:d=0.7,afade=t=out:st={max(0,total-1):.3f}:d=1",
            "-c:a", "aac", "-b:a", "160k", str(output),
        ])
    return output


def build_preview(shots: list[dict], music: Path) -> None:
    concat = EDIT / "shots.ffconcat"
    concat.write_text("\n".join(f"file '{Path(shot['file']).as_posix()}'" for shot in shots), encoding="utf-8")
    base = EDIT / "visual_master.mp4"
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", str(base),
    ])
    ass = str(CAPTIONS.resolve()).replace("\\", "/").replace(":", "\\:")
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(base),
        "-i", str(VOICE), "-i", str(music), "-filter_complex",
        f"[0:v]subtitles='{ass}'[v];[1:a]volume=1.05[a1];[2:a]volume=0.14[a2];"
        "[a1][a2]amix=inputs=2:duration=first:normalize=0[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", "-movflags", "+faststart",
        str(PREVIEW),
    ])


class Api:
    def __init__(self) -> None:
        self.process = subprocess.Popen(
            [str(CLI), "api"], cwd=str(FLOWLINE / "engine"), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1,
        )

    def request(self, payload: dict) -> dict:
        assert self.process.stdin and self.process.stdout
        self.process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.process.stdin.flush()
        reply = json.loads(self.process.stdout.readline())
        if "error" in reply:
            raise RuntimeError(reply["error"])
        return reply["result"]

    def close(self) -> None:
        if self.process.stdin:
            self.process.stdin.close()
        self.process.wait(timeout=10)


def build_flowline(shots: list[dict], music: Path, captions: list[dict]) -> None:
    if PROJECT.exists():
        raise RuntimeError(f"FlowLine project already exists: {PROJECT}")
    api = Api()
    try:
        api.request({
            "method": "project.create", "location": str(ROOT), "name": PROJECT.name,
            "video": {"width": W, "height": H, "rateNum": FPS, "rateDen": 1},
        })
        media_ids: dict[str, str] = {}
        for file in [*(Path(shot["file"]) for shot in shots), VOICE, music]:
            view = api.request({"method": "media.import", "path": str(PROJECT), "file": str(file)})
            match = next(item for item in view["project"]["media"] if Path(item["path"]) == file)
            media_ids[str(file)] = match["id"]
        for shot in shots:
            result = api.request({
                "method": "edit.apply", "path": str(PROJECT),
                "command": {"op": "addClip", "mediaId": media_ids[shot["file"]],
                            "trackId": "T1", "start": shot["start"]},
            })
            clip_id = result["createdId"]
            actual = next(clip["duration"] for clip in result["project"]["timelines"][0]["clips"] if clip["id"] == clip_id)
            if abs(actual - shot["duration"]) > 0.001:
                api.request({
                    "method": "edit.apply", "path": str(PROJECT),
                    "command": {"op": "trimClip", "clipId": clip_id, "edge": "end",
                                "delta": shot["duration"] - actual},
                })
            api.request({
                "method": "edit.apply", "path": str(PROJECT),
                "command": {"op": "updateClip", "clipId": clip_id,
                            "patch": {"name": f"{len([s for s in shots if s['start'] <= shot['start']]):02d} — {shot['label']}"}},
            })
        for file, track, volume, name in [
            (VOICE, "T2", 1.0, "ElevenLabs Narration"),
            (music, "T3", 0.14, "Background Music — Pressure Bed"),
        ]:
            result = api.request({
                "method": "edit.apply", "path": str(PROJECT),
                "command": {"op": "addClip", "mediaId": media_ids[str(file)], "trackId": track, "start": 0.0},
            })
            api.request({
                "method": "edit.apply", "path": str(PROJECT),
                "command": {"op": "updateClip", "clipId": result["createdId"],
                            "patch": {"name": name, "volume": volume, "fadeIn": 0.3, "fadeOut": 0.7}},
            })
        caption_commands = []
        for caption in captions:
            caption_commands.append({
                "op": "addTextClip", "trackId": "T4", "start": caption["start"],
                "duration": caption["duration"], "offsetY": 0.30,
                "style": {"content": caption["text"], "fontFamily": "Arial", "fontSize": 0.042,
                          "fontWeight": 800, "color": "#ffffff", "align": "center",
                          "strokeWidth": 0.006, "strokeColor": "#000000", "shadow": True},
            })
        api.request({
            "method": "edit.apply", "path": str(PROJECT),
            "command": {"op": "batch", "commands": caption_commands},
        })
        api.request({"method": "project.save", "path": str(PROJECT)})
    finally:
        api.close()


def main() -> int:
    for folder in (VO, MUSIC, EDIT, SHOTS, FINAL):
        folder.mkdir(parents=True, exist_ok=True)
    generate_voice()
    total = duration(VOICE)
    word_items = words()
    captions = caption_groups(word_items)
    write_captions(captions)
    shots = build_shots(total)
    music = build_music(total)
    plan = {
        "title": "Europe Should Be Afraid of This Barcelona Team",
        "duration": total,
        "script": SCRIPT,
        "voiceover": str(VOICE),
        "music": str(music),
        "shots": shots,
        "captions": captions,
        "flowlineProject": str(PROJECT),
        "preview": str(PREVIEW),
    }
    PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    build_preview(shots, music)
    build_flowline(shots, music, captions)
    print(json.dumps({"duration": total, "shots": len(shots), "captions": len(captions),
                      "preview": str(PREVIEW), "project": str(PROJECT)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
