from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

P = Path(r"C:\Users\Wendy\Documents\Football Channel")
VID = P / "pep_guardiola_ferran_torres_short"
V = VID / "assets" / "vo"
T = VID / "_tmp"
F = VID / "final video"
OUT = F / "pep_guardiola_ferran_torres_9x16.mp4"
OUT_CAPS = F / "pep_guardiola_ferran_torres_9x16_captions.mp4"
ASS = F / "captions.ass"
FF = r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

# Timeline: (segment, start_offset) in final video. VO segments get captions.
# hook 0-13.8, goal_insert 13.8-24.0, story 24.0-41.2, pep_insert 41.2-57.2, payoff 57.2-78.4
TIMELINE = [
    ("vo_hook", 0.0, 13.8),
    ("goal_insert", 13.8, 24.0),
    ("vo_story", 24.0, 41.2),
    ("pep_insert", 41.2, 57.2),
    ("vo_payoff", 57.2, 78.4),
]

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


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stderr[-800:])
        sys.exit(1)
    return r


def dur(p):
    if not p.exists():
        return 0.0
    r = subprocess.run([FF, "-i", str(p)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


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


def caption_groups(name, text, offset):
    """Word-timed caption groups, fallback to even split."""
    words_from_text = re.findall(r"[A-Za-z0-9']+", text.upper())
    audio = V / f"{name}.mp3"
    audio_dur = dur(audio)
    timed_words = None
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(
            str(audio), beam_size=5, language="en", word_timestamps=True, vad_filter=False
        )
        tw = []
        for seg in segments:
            for word in getattr(seg, "words", []) or []:
                token = re.sub(r"[^A-Z0-9']+", "", str(word.word).upper())
                if token:
                    tw.append((float(word.start), float(word.end), token))
        if tw:
            timed_words = tw
    except Exception as exc:
        print(f"  whisper fallback for {name}: {exc}")

    group_size = 2
    if timed_words:
        groups = []
        total_script = len(words_from_text)
        total_timed = len(timed_words)
        for index in range(0, total_script, group_size):
            script_chunk = words_from_text[index : index + group_size]
            s0 = min(total_timed - 1, max(0, round(index * total_timed / total_script)))
            s1 = min(
                total_timed - 1,
                max(s0, round((min(total_script, index + group_size) * total_timed) / total_script) - 1),
            )
            groups.append((offset + timed_words[s0][0], offset + timed_words[s1][1], " ".join(script_chunk)))
        return groups

    chunks = [" ".join(words_from_text[i : i + group_size]) for i in range(0, len(words_from_text), group_size)]
    if not chunks or audio_dur <= 0:
        return []
    slice_dur = audio_dur / len(chunks)
    groups = []
    cursor = offset
    for chunk in chunks:
        groups.append((cursor, cursor + slice_dur, chunk))
        cursor += slice_dur
    return groups


def main():
    events = []
    for name, start, end in TIMELINE:
        if name.startswith("vo_"):
            for gs, ge, text in caption_groups(name, VO_TEXTS[name], start):
                if ge <= gs:
                    continue
                events.append(
                    "Dialogue: 0,"
                    f"{ass_time(gs)},{ass_time(ge)},Hormozi,,0,0,0,,"
                    "{\\fad(25,25)\\t(0,70,\\fscx112\\fscy112)\\t(70,150,\\fscx100\\fscy100)}"
                    + text
                )

    content = "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            (
                "Style: Hormozi,"
                "Arial Black,72,&H0000E6FF,&H000000FF,"
                "&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,"
                "8,4,2,60,60,110,1"
            ),
            "[Events]",
            "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
            *events,
            "",
        ]
    )
    ASS.write_text(content, encoding="utf-8")
    print(f"Wrote {ASS} with {len(events)} caption events")

    ass_filter = str(ASS).replace("\\", "/").replace(":", "\\:")
    print("Burning captions...")
    run([
        FF, "-y", "-i", str(OUT),
        "-vf", f"ass='{ass_filter}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(OUT_CAPS),
    ])
    print(f"DONE: {OUT_CAPS}")
    print(f"  Size: {OUT_CAPS.stat().st_size // 1024 // 1024} MB")
    print(f"  Duration: {dur(OUT_CAPS):.1f}s")


if __name__ == "__main__":
    main()
