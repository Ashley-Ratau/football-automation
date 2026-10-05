from __future__ import annotations
import json, os, re, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

P = Path(r"C:\Users\Wendy\Documents\Football Channel")
VID = P / "pep_guardiola_ferran_torres_short"
A = VID / "assets"
B = A / "broll"
I = A / "inserts"
V = A / "vo"
T = VID / "_tmp"
F = VID / "final video"
for d in (A, B, I, V, T, F, VID / "assets" / "raw"):
    d.mkdir(parents=True, exist_ok=True)
OUT = F / "pep_guardiola_ferran_torres_9x16.mp4"
FF = r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
ENV = P / "work" / "secrets" / ".env.local"
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "bu5eKETbFKC8G702EAU4")

VF = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"

RAW = VID / "assets" / "raw"


def run(cmd, check=True):
    print(">", " ".join(map(str, cmd))[:200], flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("  FAILED:", r.stderr[-500:])
        sys.exit(1)
    return r


def dur(p):
    if not p.exists():
        return 0
    r = subprocess.run([FF, "-i", str(p)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        return 0
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def download(url, out_path):
    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"  SKIP download {out_path.name} (exists)")
        return
    print(f"  Downloading {url}...")
    run(["yt-dlp", "--extractor-args", "youtube:player_client=android", "-f", "best[height<=720]", "-o", str(out_path), url, "--merge-output-format", "mp4"])


def tts(name, text):
    out = V / f"{name}.mp3"
    if out.exists() and out.stat().st_size > 10000:
        return out
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is missing from work/secrets/.env.local.")
    import base64
    import json as _json
    import urllib.error
    import wave
    raw = out.with_suffix(".raw.wav")
    model_id = "gemini-3.1-flash-tts-preview"
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
            "x-goog-api-key": gemini_key,
            "Content-Type": "application/json",
            "Api-Revision": "2026-05-20",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = _json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini TTS failed: HTTP {exc.code}: {body}") from exc

    audio = None
    for step in result.get("steps", []):
        for item in step.get("content", []):
            if item.get("type") == "audio" and item.get("data"):
                audio = item
                break
        if audio:
            break
    if not audio:
        raise RuntimeError("Gemini TTS completed without an audio payload.")
    if audio.get("mime_type") != "audio/l16":
        raise RuntimeError(f"Unsupported Gemini TTS audio type: {audio.get('mime_type')!r}.")

    pcm = base64.b64decode(audio["data"])
    channels = int(audio.get("channels", 1))
    sample_rate = int(audio.get("sample_rate", 24000))
    with wave.open(str(raw), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm)

    run([
        FF, "-y", "-i", str(raw),
        "-filter:a", "atempo=1.2,volume=10dB,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120,alimiter=limit=0.97",
        "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-q:a", "2",
        str(out),
    ])
    return out


def render_clip(source, ss, length, out_path, with_audio=False):
    if out_path.exists() and dur(out_path) > length - 0.5:
        return
    cmd = [FF, "-y", "-ss", str(ss), "-i", str(source), "-t", str(length), "-vf", VF]
    if with_audio:
        fade_out = max(0.0, length - 0.5)
        cmd += [
            "-af", f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_out:.3f}:d=0.5",
            "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "44100",
        ]
    else:
        cmd += ["-an"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", str(out_path)]
    run(cmd)


def build_broll_montage(sources, target_dur, out_path):
    """Build a b-roll montage cycling through (source, start) pairs."""
    if out_path.exists() and dur(out_path) > target_dur - 0.5:
        return
    parts = []
    remain = target_dur + 0.3
    i = 0
    while remain > 0:
        src, start = sources[i % len(sources)]
        sd = dur(src)
        if sd < 2:
            i += 1
            continue
        start = float(start) % max(1, sd - 4)
        length = min(5.0, remain)
        o = T / f"broll_{out_path.stem}_{i:02d}.mp4"
        render_clip(src, start, length, o)
        parts.append(o)
        remain -= length
        i += 1
    lst = T / f"broll_{out_path.stem}_list.txt"
    lst.write_text("\n".join(f"file '{x.resolve()}'" for x in parts), encoding="utf-8")
    visual = T / f"broll_{out_path.stem}_concat.mp4"
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-t", str(target_dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an",
         str(visual)])
    return visual


def render_vo_segment(sources, audio_path, out_path):
    """Render a VO segment: b-roll montage + voiceover."""
    target = dur(audio_path)
    if target < 0.5:
        print(f"  WARNING: {audio_path.name} has no duration")
        return None
    visual = build_broll_montage(sources, target, T / f"vis_{out_path.stem}.mp4")
    if visual is None:
        return None
    run([FF, "-y", "-i", str(visual), "-i", str(audio_path),
         "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "44100", "-shortest",
         str(out_path)])
    return out_path


# ============================================================
# YOUTUBE SOURCES
# ============================================================

YOUTUBE_URLS = {
    "ferran_interview": (
        "https://www.youtube.com/watch?v=VFnJIHVynpg",
        RAW / "ferran_interview.mp4",
    ),
    "pep_ferran_presser": (
        "https://www.youtube.com/watch?v=yP8pYFObuO0",
        RAW / "pep_ferran_presser.mp4",
    ),
    "ferran_wc_goal": (
        "https://www.youtube.com/watch?v=e6a6lppWZkQ",
        RAW / "ferran_wc_goal.mp4",
    ),
    "spain_highlights": (
        "https://www.youtube.com/watch?v=eBItTZ7sU4A",
        RAW / "spain_highlights.mp4",
    ),
    "ferran_season": (
        "https://www.youtube.com/watch?v=3sxskI37Aec",
        RAW / "ferran_season.mp4",
    ),
}

# ============================================================
# VOICEOVER SCRIPT
# ============================================================

VO_TEXTS = {
    "vo_hook": (
        "Pep Guardiola warned us about Ferran Torres. He was right. "
        "The proof came in the 106th minute of the World Cup final. "
        "A substitute who had been written off. A single left-footed volley. "
        "And Spain were world champions."
    ),
    "vo_story": (
        "But to understand that moment, you need to go back. "
        "Ferran was nineteen, alone in Manchester during the pandemic. "
        "Quarantined for two weeks. Could not speak English. His family was hours away. "
        "The Premier League was faster and more brutal than anything he had faced. "
        "Yet Pep Guardiola saw it clearly."
    ),
    "vo_payoff": (
        "When Barcelona came calling, Pep could have stopped it. "
        "Instead he said: it is my club. My Barça. "
        "As long as the teams agree, you can leave. "
        "And Ferran walked into history. "
        "From a teenager who could not order food in English, "
        "to the man who scored the winning goal in a World Cup final. "
        "Pep warned us. He was right."
    ),
}


def main():
    print("=" * 60)
    print("Pep Guardiola Warned Us About Ferran Torres (v2)")
    print("=" * 60)

    # Step 0: Download YouTube clips
    print("\n=== Download clips ===")
    for name, (url, path) in YOUTUBE_URLS.items():
        download(url, path)

    # Step 1: Voiceover
    print("\n=== Voiceover ===")
    vos = {}
    for name, text in VO_TEXTS.items():
        vos[name] = tts(name, text)
        print(f"  {name}: {dur(vos[name]):.1f}s")

    # Step 2: Prepare inserts
    print("\n=== Inserts ===")

    # Insert 1: World Cup goal (match footage, full audio)
    goal_insert = I / "wc_goal_insert.mp4"
    goal_src = RAW / "ferran_wc_goal.mp4"
    if goal_src.exists() and dur(goal_src) > 2:
        gd = min(14.0, dur(goal_src))
        render_clip(goal_src, 0, gd, goal_insert, with_audio=True)
        goal_dur = dur(goal_insert) or gd
    else:
        # Fallback: extract goal moment from Spain highlights (goal ~1:25 into 1:58 video)
        fallback = RAW / "spain_highlights.mp4"
        if fallback.exists() and dur(fallback) > 30:
            gd = min(14.0, dur(fallback) - 85)
            render_clip(fallback, 85, gd, goal_insert, with_audio=True)
            goal_dur = dur(goal_insert) or gd
            print(f"  Used highlights fallback for goal insert: {goal_dur:.1f}s (start=85s)")
        else:
            print("  WARNING: goal clip missing/unavailable")
            goal_dur = 10.0

    # Insert 2: Pep Guardiola talking about Ferran.
    # Subtitle timeline: journalist names Ferran Torres at ~10:10
    # ("nothing is official when it comes to Ferran Torres..."), Pep answers
    # "Absolutely not. I want the happiness of my players... if you are not
    # happy, you have to leave." running through ~10:26.
    pep_insert = I / "pep_insert.mp4"
    pep_src = RAW / "pep_ferran_presser.mp4"
    if pep_src.exists() and dur(pep_src) > 2:
        pd = min(16.0, dur(pep_src))
        ps = 610.0  # 10:10, the Ferran question/answer moment
        render_clip(pep_src, ps, pd, pep_insert, with_audio=True)
        pep_dur = dur(pep_insert) or pd
    else:
        print("  WARNING: pep clip missing/unavailable")
        pep_dur = 12.0

    # Step 3: Render VO segments with proper b-roll
    print("\n=== VO segments ===")

    ferran_int = RAW / "ferran_interview.mp4"
    ferran_season = RAW / "ferran_season.mp4"
    spain_hl = RAW / "spain_highlights.mp4"
    wc_goal = RAW / "ferran_wc_goal.mp4"

    # VO 1 - Hook: interview b-roll (Ferran centered, clear)
    hook_srcs = []
    if ferran_int.exists():
        hook_srcs.append((ferran_int, 10))
    if ferran_season.exists():
        hook_srcs.append((ferran_season, 30))
    if not hook_srcs:
        print("ERROR: no b-roll for hook")
        sys.exit(1)
    seg_hook = T / "segment_hook.mp4"
    render_vo_segment(hook_srcs, vos["vo_hook"], seg_hook)

    # VO 2 - Story: interview b-roll (Ferran centered, clear)
    story_srcs = []
    if ferran_int.exists():
        story_srcs.append((ferran_int, 30))
    if ferran_season.exists():
        story_srcs.append((ferran_season, 60))
    if ferran_int.exists():
        story_srcs.append((ferran_int, 120))
    if ferran_season.exists():
        story_srcs.append((ferran_season, 120))
    if not story_srcs:
        print("ERROR: no b-roll for story")
        sys.exit(1)
    seg_story = T / "segment_story.mp4"
    render_vo_segment(story_srcs, vos["vo_story"], seg_story)

    # VO 3 - Payoff: match footage + interview mix
    payoff_srcs = []
    if spain_hl.exists():
        payoff_srcs.append((spain_hl, 25))
    if ferran_int.exists():
        payoff_srcs.append((ferran_int, 60))
    if wc_goal.exists():
        payoff_srcs.append((wc_goal, 0))
    if spain_hl.exists():
        payoff_srcs.append((spain_hl, 5))
    if not payoff_srcs:
        print("ERROR: no b-roll for payoff")
        sys.exit(1)
    seg_payoff = T / "segment_payoff.mp4"
    render_vo_segment(payoff_srcs, vos["vo_payoff"], seg_payoff)

    # Step 4: Assemble
    print("\n=== Assemble ===")

    # Timeline: hook -> goal_insert -> story -> pep_insert -> payoff
    timeline = [seg_hook, goal_insert, seg_story, pep_insert, seg_payoff]
    for p in timeline:
        if not p.exists():
            print(f"  WARNING: {p.name} missing, skipping")

    lst = T / "final_concat.txt"
    existing = [p for p in timeline if p.exists()]
    lst.write_text("\n".join(f"file '{p.resolve()}'" for p in existing), encoding="utf-8")

    run([
        FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "44100", "-pix_fmt", "yuv420p",
        str(OUT),
    ])

    total = dur(OUT)
    m, s = divmod(int(total), 60)
    print(f"\n{'=' * 60}")
    print(f"  DONE: {OUT.name}")
    print(f"  Duration: {m}:{s:02d} ({total:.1f}s)")
    print(f"  Size: {OUT.stat().st_size // 1024 // 1024} MB")
    print(f"{'=' * 60}")

    # QC: extract one frame every 5 seconds for visual inspection
    q = F / "qc"
    q.mkdir(exist_ok=True)
    step = 5
    t = 0.0
    while t < total:
        qf = q / f"frame_{int(t):04d}s.jpg"
        if not qf.exists():
            run([FF, "-y", "-ss", str(t), "-i", str(OUT),
                 "-frames:v", "1", "-update", "1", str(qf)], check=False)
        t += step

    # QC: one labeled frame per timeline segment
    labels = ["hook", "goal_insert", "story", "pep_insert", "payoff"]
    acc = 0.0
    for label, p in zip(labels, timeline):
        if p.exists():
            seg_mid = acc + dur(p) / 2
            run([FF, "-y", "-ss", str(seg_mid), "-i", str(OUT),
                 "-frames:v", "1", "-update", "1", str(q / f"{label}.jpg")], check=False)
            acc += dur(p)

    report = {
        "title": "Pep Guardiola Warned Us About Ferran Torres. He Was Right.",
        "output": str(OUT),
        "duration_seconds": round(total, 2),
        "resolution": "1080x1920 (9x16)",
        "voice_id": VOICE,
        "segments": ["interview_broll", "match_goal", "interview_broll", "pep_presser", "match+interview"],
    }
    (F / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
