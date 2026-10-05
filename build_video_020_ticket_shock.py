from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "work"))

import football_short_automation as auto  # noqa: E402


TITLE = "FIFA Priced Out Its Own World Cup Opener"
PROJECT = ROOT / "Video 020 - FIFA Priced Out Its Own World Cup Opener"


PLAN = {
    "folder_title": PROJECT.name,
    "project_title": TITLE,
    "upload_title": TITLE,
    "topic_summary": (
        "Fresh World Cup ticket-pricing story: reports on June 10-12, 2026 said the "
        "USA-Paraguay World Cup opener at SoFi Stadium still had unsold seats while "
        "premium prices and resale inventory stayed extremely high."
    ),
    "description": (
        "The 2026 World Cup is supposed to be football's biggest party in America, "
        "but the USA opener has exposed a brutal ticket-pricing problem. Reports "
        "from talkSPORT, The Sun and the New York Post point to dynamic pricing, "
        "very expensive seats, and unsold inventory around USA vs Paraguay at SoFi Stadium.\n\n"
        "Sources reviewed: talkSPORT, The Sun, New York Post, public venue/team references.\n\n"
        "#WorldCup #USMNT #Football #Soccer #Shorts"
    ),
    "tags": [
        "World Cup 2026",
        "FIFA",
        "USMNT",
        "USA Paraguay",
        "football shorts",
        "soccer news",
        "SoFi Stadium",
        "World Cup tickets",
        "football",
        "shorts",
    ],
    "script_sections": [
        {
            "id": 1,
            "text": (
                "America waited years for a home World Cup. And now FIFA may have priced "
                "its own opener into silence. USA versus Paraguay at SoFi should feel like "
                "a coronation. Instead, the story is empty seats."
            ),
            "image_entities": ["SoFi Stadium", "United States men's national soccer team"],
        },
        {
            "id": 2,
            "text": (
                "The problem is not interest. It is the math. Reports say top seats for "
                "the USA opener climbed into the thousands, final tickets were listed near "
                "luxury-car money, and official resale pages still showed huge inventory. "
                "That is how you turn the people's game into a corporate waiting room."
            ),
            "image_entities": ["SoFi Stadium", "Tim Weah", "Mauricio Pochettino"],
        },
        {
            "id": 3,
            "text": (
                "And this is the warning for the whole tournament. If the host nation can "
                "open a World Cup with fans priced out, FIFA did not just misread America. "
                "It forgot why World Cups feel massive in the first place."
            ),
            "image_entities": ["FIFA World Cup Trophy", "SoFi Stadium"],
        },
    ],
    "insert_clips": [
        {
            "after_section_id": 1,
            "target_duration": 4.6,
            "type": "proof_card",
            "source_note": "No usable external video insert was downloadable in this sandbox; yt-dlp is blocked by Access denied.",
        }
    ],
    "thumbnail_options": [
        {
            "headline": "PRICED OUT",
            "left_subject": "SoFi Stadium",
            "center_subject": "United States men's national soccer team",
            "right_subject": "FIFA World Cup Trophy",
        },
        {
            "headline": "EMPTY SEATS?",
            "left_subject": "SoFi Stadium",
            "center_subject": "Tim Weah",
            "right_subject": "Mauricio Pochettino",
        },
        {
            "headline": "FIFA'S WARNING",
            "left_subject": "FIFA World Cup Trophy",
            "center_subject": "SoFi Stadium",
            "right_subject": "",
        },
    ],
}

SOURCES = [
    {
        "title": "talkSPORT: FIFA accused of pricing out fans",
        "url": "https://talksport.com/football/world-cup/4321574/usmnt-ticket-prices-los-angeles-paraguay-unaffordable-sofi-stadium/",
        "note": "June 12, 2026 report on dynamic pricing, USA opener prices, and unsold resale inventory.",
    },
    {
        "title": "The Sun: USA opener not sold out",
        "url": "https://www.the-sun.com/sport/16474160/usa-empty-seats-world-cup-paraguay-not-sold-out/",
        "note": "June 10, 2026 report that USA vs Paraguay at SoFi had tickets still available.",
    },
    {
        "title": "New York Post: free-ticket glitch and pricing scrutiny",
        "url": "https://nypost.com/2026/06/05/sports/fifa-accidentally-gives-fans-free-2026-world-cup-tickets/",
        "note": "June 5, 2026 report on ticketing errors, investigations, and dynamic-pricing context.",
    },
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_docs(project: Path) -> None:
    write(
        project / "01 idea brief.md",
        """# Idea Brief

## Suggested ideas reviewed
- FIFA priced out its own USA opener: best mix of urgency, conflict, and proof.
- Canada pressure before its home opener: timely, but softer conflict.
- Scotland/Haiti underdog opener: good football romance, weaker hard hook today.
- SoFi stadium controversy: relevant, but too infrastructure-heavy alone.

## Chosen idea
FIFA priced out its own World Cup opener.

## Why it wins
The angle is current, emotionally clear, and built around irony: a home World Cup opener that should be packed is instead being discussed through price shock and unsold seats.
""",
    )
    source_lines = "\n".join(f"- [{s['title']}]({s['url']}): {s['note']}" for s in SOURCES)
    write(
        project / "02 research dossier.md",
        f"""# Research Dossier

## Topic
{PLAN['topic_summary']}

## Sources checked
{source_lines}

## Clip validation
External YouTube clip search was attempted for ticket-price reactions and Pochettino/Weah ticket comments, but the local `yt-dlp.exe` path returned `Access is denied`. Because that makes clip acquisition unverifiable in this sandbox, the final edit uses a sourced proof-card insert instead of claiming a real pundit/player clip exists.

## Freshness check
This does not reuse the existing local Shorts on Norway, Ronaldo, Yamal, Real Madrid/Atletico, Tuchel/Saka, World Cup visa chaos, Mourinho, Messi, Kane, FIFA halftime show, Foden/Palmer, World Cup stats, or generic World Cup scale.
""",
    )
    auto.write_markdown(project / "03 script.md", auto.render_script_markdown(PLAN))
    auto.write_markdown(project / "04 upload metadata.md", auto.make_upload_metadata(PLAN))
    write(
        project / "05 clip sourcing plan.md",
        """# Clip Sourcing Plan

## Narrative insert
- `proof_insert_ticket_prices.mp4`
- Placement: immediately after the opening hook.
- Purpose: verify the premise with ticket-price and unsold-seat evidence.
- Audio: keep a subtle insert sound bed only; no voiceover under this segment.
- Note: this is a proof-card insert because external video download was blocked.

## B-roll
- SoFi Stadium stills/animated crops: establish the USA opener location.
- USMNT/player stills: connect the story to the host nation.
- Trophy/ticket graphics: support the FIFA/tournament stakes.
- All B-roll is muted and kept short. No FIFA or UEFA B-roll clips are used.
""",
    )
    write(
        project / "07 edit brief.md",
        """# Edit Brief

## Structure
1. Hook voiceover over SoFi/USMNT visuals.
2. Hard cut to sourced proof insert for the pricing/unsold-seat premise.
3. Return to voiceover for the price math and fan-access argument.
4. End on the tournament-wide warning.

## Pacing
Clean, serious, and slightly angry. No captions. Use fast still movement and proof graphics, not random filler.

## Thumbnail
Communicate price shock and empty-seat risk: big readable text, SoFi/USMNT context, World Cup stakes.
""",
    )


def make_proof_insert(paths: dict[str, Path]) -> Path:
    card = paths["graphics"] / "proof_insert_ticket_prices.png"
    auto.build_text_card(
        "USA OPENER\nSTILL NOT SOLD OUT",
        "Reports cited huge resale inventory and prices in the thousands",
        card,
        accent="#f97316",
    )
    out = paths["editor_inserts"] / "proof_insert_ticket_prices.mp4"
    cmd = [
        auto.ffmpeg_exe(),
        "-y",
        "-loop",
        "1",
        "-i",
        str(card),
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=92:duration=4.6",
        "-t",
        "4.6",
        "-vf",
        "scale=1080:1920,setsar=1",
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
        "96k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    return out


def ffprobe_streams(path: Path) -> dict:
    proc = subprocess.run(
        [auto.ffmpeg_exe(), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    media = proc.stderr + proc.stdout
    duration = auto.ffprobe_duration(path)
    return {
        "format": {"duration": duration},
        "streams": [
            {"codec_type": "video"} if " Video:" in media else {},
            {"codec_type": "audio"} if " Audio:" in media else {},
        ],
    }


def script_sections(project: Path) -> list[str]:
    text = (project / "03 script.md").read_text(encoding="utf-8")
    body = text.split("# Full Voiceover Script", 1)[1].strip()
    return [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]


def synthesize_sapi_mp3(text: str, output: Path, tmp: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    text_path = tmp / f"{output.stem}.txt"
    wav_path = tmp / f"{output.stem}.wav"
    ps_path = tmp / "sapi_voiceover.ps1"
    text_path.write_text(text, encoding="utf-8")
    ps_path.write_text(
        "param([string]$TextPath,[string]$OutPath)\n"
        "Add-Type -AssemblyName System.Speech\n"
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
        "$synth.Rate = 2\n"
        "$synth.Volume = 100\n"
        "$text = Get-Content -LiteralPath $TextPath -Raw\n"
        "$synth.SetOutputToWaveFile($OutPath)\n"
        "$synth.Speak($text)\n"
        "$synth.Dispose()\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_path), str(text_path), str(wav_path)],
        check=True,
    )
    subprocess.run(
        [auto.ffmpeg_exe(), "-y", "-i", str(wav_path), "-vn", "-c:a", "libmp3lame", "-q:a", "2", str(output)],
        check=True,
    )


def synthesize_fallback_voice(project: Path) -> None:
    out_dir = project / "assets" / "voiceover" / "elevenlabs"
    tmp = project / "_tmp"
    chunks = script_sections(project)
    chunk_paths = []
    for idx, chunk in enumerate(chunks, 1):
        output = out_dir / f"elevenlabs_part_{idx:02d}.mp3"
        synthesize_sapi_mp3(chunk, output, tmp)
        chunk_paths.append(output)
    list_path = out_dir / "concat_list.txt"
    list_path.write_text("\n".join(f"file '{path.as_posix()}'" for path in chunk_paths), encoding="utf-8")
    subprocess.run(
        [
            auto.ffmpeg_exe(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            str(out_dir / "voiceover_elevenlabs_full.mp3"),
        ],
        check=True,
    )
    (out_dir / "voiceover_narration_clean.txt").write_text("\n\n".join(chunks), encoding="utf-8")
    (out_dir / "OFFLINE_FALLBACK_VOICE_USED.txt").write_text(
        "Approved ElevenLabs voice generation failed with a network/socket permissions block. "
        "This local draft uses Windows SAPI fallback audio and must not be uploaded.\n",
        encoding="utf-8",
    )


def main() -> None:
    auto.load_env_files()
    if PROJECT.exists():
        shutil.rmtree(PROJECT)
    PROJECT.mkdir(parents=True)
    paths = auto.make_dirs(PROJECT)
    write_docs(PROJECT)
    auto.save_plan_json(PROJECT, PLAN, [])

    voice_mode = "elevenlabs"
    try:
        auto.generate_voiceover(PROJECT, "bu5eKETbFKC8G702EAU4")
    except Exception as exc:  # noqa: BLE001
        voice_mode = "offline_fallback"
        write(
            PROJECT / "assets" / "voiceover" / "ELEVENLABS_BLOCKED.txt",
            f"ElevenLabs approved voice generation failed, so this run is local-only and not uploadable.\n\nError:\n{exc}",
        )
        synthesize_fallback_voice(PROJECT)
    auto.speed_adjust_voiceover(PROJECT, 1.2)

    portraits = auto.gather_portraits(paths, PLAN)
    if not portraits:
        fallback = paths["graphics"] / "fallback_card.png"
        auto.build_text_card("WORLD CUP\nPRICE SHOCK", "USA opener ticket problem", fallback, accent="#f97316")
        portraits["fallback"] = fallback

    insert = make_proof_insert(paths)
    thumb = auto.build_thumbnail_variants(PROJECT, PLAN, portraits)
    final_video = auto.build_final_video(PROJECT, PLAN, portraits, insert)
    streams = ffprobe_streams(final_video)
    duration = float(streams.get("format", {}).get("duration", 0))
    has_video = any(s.get("codec_type") == "video" for s in streams.get("streams", []))
    has_audio = any(s.get("codec_type") == "audio" for s in streams.get("streams", []))
    if not has_video or not has_audio or duration >= 60:
        raise RuntimeError(f"Verification failed: duration={duration} has_video={has_video} has_audio={has_audio}")

    verification = {
        "final_video": str(final_video),
        "thumbnail": str(thumb),
        "duration_seconds": duration,
        "has_video": has_video,
        "has_audio": has_audio,
        "voice_mode": voice_mode,
        "uploadable": voice_mode == "elevenlabs",
        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    write(PROJECT / "final video" / "verification.json", json.dumps(verification, indent=2))
    if voice_mode != "elevenlabs":
        record_dir = PROJECT / "final video" / "upload records"
        write(
            record_dir / f"{time.strftime('%Y-%m-%d')}-not-uploaded-elevenlabs-blocked.md",
            """# Not Uploaded

Reason: approved ElevenLabs voice generation was blocked by the current network/socket permissions. The rendered MP4 is a verified local draft with fallback Windows SAPI audio, so it does not meet the channel's upload criteria.

Next step: rerun this build when ElevenLabs API access is available, then upload the verified ElevenLabs version publicly.
""",
        )
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
