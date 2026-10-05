from __future__ import annotations

import json
import mimetypes
import shutil
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "Video 003 - Gary Neville Warned Us About Ronaldo"
DELIVERY = ROOT / "Editor Deliveries" / "Gary Neville Tried To Warn Us About Cristiano Ronaldo - Editor Package"
PDF_PATH = DELIVERY / "00 Instructions" / "Editor Instructions - Ronaldo Portugal Warning.pdf"


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_files(src: Path, dst: Path, patterns: tuple[str, ...]) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for path in sorted(src.glob(pattern)):
            if path.is_file():
                copy_file(path, dst / path.name)


def clean_delivery() -> None:
    if DELIVERY.exists():
        shutil.rmtree(DELIVERY)
    DELIVERY.mkdir(parents=True, exist_ok=True)


def build_delivery_folder() -> None:
    clean_delivery()

    copy_files(PROJECT / "assets" / "editor_package" / "voiceover", DELIVERY / "01 Voiceover", ("*.mp3", "*.md", "*.txt"))
    copy_files(PROJECT / "assets" / "editor_package" / "narrative_inserts", DELIVERY / "02 Narrative Insert Clips", ("*.mp4", "*.md"))
    copy_files(PROJECT / "assets" / "editor_package" / "broll_safe" / "short_clips", DELIVERY / "03 B-Roll Short Clips", ("*.mp4", "*.md"))
    copy_files(PROJECT / "assets" / "raw_sources" / "broll", DELIVERY / "04 Longer B-Roll Source Clips", ("*.mp4", "*.md", "*.vtt"))
    copy_files(PROJECT / "assets" / "editor_package" / "graphics", DELIVERY / "05 Graphics", ("*.png", "*.md"))
    copy_files(PROJECT / "assets" / "thumbnail", DELIVERY / "06 Thumbnail Options", ("*.png", "*.jpg", "*.jpeg", "*.md"))

    backups = DELIVERY / "00 Instructions" / "Markdown Backups"
    for rel in [
        "CapCut Workflow/EDITOR_HANDOFF.md",
        "CapCut Workflow/07 Edit Guides/CAPCUT_TIMELINE_GUIDE.md",
        "assets/editor_package/narrative_inserts/PLACEMENT_GUIDE.md",
        "assets/editor_package/broll_safe/short_clips/SHORT_CLIP_INDEX.md",
        "03 script.md",
        "04 upload metadata.md",
    ]:
        copy_file(PROJECT / rel, backups / Path(rel).name)


def para(text: str, style):
    return Paragraph(text.replace("&", "&amp;"), style)


def make_table(rows, widths, styles, small=False):
    body_style = styles["Small"] if small else styles["Tight"]
    table = Table([[para(str(cell), body_style) for cell in row] for row in rows], colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_pdf() -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.4, leading=9))
    styles.add(ParagraphStyle(name="Tight", parent=styles["BodyText"], fontSize=9, leading=11))
    styles.add(ParagraphStyle(name="TitleClean", parent=styles["Title"], fontSize=18, leading=22, textColor=colors.black))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=12, leading=15, spaceBefore=9, textColor=colors.black))

    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, rightMargin=0.45 * inch, leftMargin=0.45 * inch, topMargin=0.45 * inch, bottomMargin=0.45 * inch)
    story = [
        para("Editor Instructions: Gary Neville Tried To Warn Us About Cristiano Ronaldo", styles["TitleClean"]),
        para("CapCut assembly guide for the Ronaldo / Portugal World Cup warning video.", styles["BodyText"]),
        Spacer(1, 0.12 * inch),
    ]

    story.append(para("1. Folder Map", styles["Section"]))
    story.append(
        make_table(
            [
                ["Folder", "Purpose"],
                ["01 Voiceover", "Main ElevenLabs V3 narration. Put this on the main audio track first."],
                ["02 Narrative Insert Clips", "Actual cutaway clips where voiceover should pause or dip and clip audio should play."],
                ["03 B-Roll Short Clips", "Muted short clips for fast visual pacing over the narration."],
                ["04 Longer B-Roll Source Clips", "Longer backup source clips if more B-roll is needed."],
                ["05 Graphics", "Simple graphic cards: warning timeline, Portugal talent map, weapon vs system."],
                ["06 Thumbnail Options", "Three thumbnail drafts. Recommended: thumbnail_v1_he_knew.png."],
            ],
            [1.75 * inch, 5.85 * inch],
            styles,
        )
    )

    story.append(para("2. Main Edit Rules", styles["Section"]))
    story.append(
        make_table(
            [
                ["Rule", "Instruction"],
                ["No FIFA clips", "Avoid FIFA footage because previous uploads triggered copyright restrictions."],
                ["Pacing", "Change visuals every sentence or two. Most B-roll should last 2-6 seconds."],
                ["Narrative inserts", "Use these as proof moments. Keep them short and let the original audio play."],
                ["Tone", "Respectful but urgent. This is not anti-Ronaldo; it is a Portugal World Cup warning."],
                ["Graphics", "Use each graphic for 5-8 seconds with a slight zoom or push-in."],
            ],
            [1.55 * inch, 6.05 * inch],
            styles,
        )
    )

    story.append(para("3. Timeline Guide", styles["Section"]))
    story.append(
        make_table(
            [
                ["Time", "Voiceover Section", "Visual Plan"],
                ["00:00-00:55", "Chile friendly hook and missed pass/shot setup.", "Use B-roll 001, 002, 003. Add quick text flashes."],
                ["00:55-01:20", "Gary Neville tried to warn us.", "Insert: neville_not_accepting_end_02m04s-02m20s.mp4."],
                ["01:20-02:45", "Ronaldo gravity and old rules.", "Use B-roll 004, 005, 006, 007."],
                ["02:45-03:45", "Portugal's talent list.", "Use B-roll 015, 014, 017, 018 and graphic_portugal_talent_map.png."],
                ["03:45-05:05", "Chile friendly and Qatar 2022 lesson.", "Use B-roll 009, 010, 022 and graphic_warning_timeline.png."],
                ["05:05-05:35", "Neville warning sounds louder now.", "Insert: keane_neville_accept_less_games_00m31s-00m53s.mp4."],
                ["06:45-07:25", "Portugal may be better balanced without him.", "Insert: danny_mills_portugal_better_without_00m34s-01m42s.mp4. Use strongest 15-25 sec."],
                ["08:45-09:25", "Weapon vs system solution.", "Use graphic_weapon_vs_system.png, then ESPN bench acceptance insert."],
                ["10:15-10:45", "Emotional gravity around Ronaldo.", "Insert: ronaldo_blanks_neville_00m00s-00m18s.mp4. Use 5-8 sec if pacing is tight."],
                ["10:45-11:27", "Final World Cup question.", "Use B-roll 013, 023, optional 021. End with bold final text."],
            ],
            [0.9 * inch, 2.4 * inch, 4.3 * inch],
            styles,
            small=True,
        )
    )

    story.append(para("4. Final Export", styles["Section"]))
    story.append(
        make_table(
            [
                ["Setting", "Value"],
                ["Format", "MP4"],
                ["Resolution", "1920x1080"],
                ["Audio", "Voiceover clear and dominant; insert audio only during insert moments."],
                ["Save location", "final video/capcut export"],
            ],
            [1.55 * inch, 6.05 * inch],
            styles,
        )
    )
    doc.build(story)


def upload_to_drive() -> dict:
    sys.path.insert(0, str(ROOT / "work"))
    from googleapiclient.http import MediaFileUpload
    from youtube_oauth_tool import drive_service

    service = drive_service()

    def create_folder(name: str, parent_id: str | None = None) -> dict:
        metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            metadata["parents"] = [parent_id]
        return service.files().create(body=metadata, fields="id,name,webViewLink").execute()

    def upload_file(path: Path, parent_id: str) -> dict:
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        metadata = {"name": path.name, "parents": [parent_id]}
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=True)
        return service.files().create(body=metadata, media_body=media, fields="id,name,mimeType,webViewLink").execute()

    root = create_folder(DELIVERY.name)
    folder_ids = {DELIVERY: root["id"]}
    uploaded = []
    for folder in sorted([p for p in DELIVERY.rglob("*") if p.is_dir()]):
        folder_ids[folder] = create_folder(folder.name, folder_ids[folder.parent])["id"]
    for file_path in sorted([p for p in DELIVERY.rglob("*") if p.is_file()]):
        uploaded.append(upload_file(file_path, folder_ids[file_path.parent]))
    service.permissions().create(fileId=root["id"], body={"type": "anyone", "role": "reader"}, fields="id").execute()
    manifest = {
        "drive_folder": root,
        "uploaded_file_count": len(uploaded),
        "local_delivery_folder": str(DELIVERY),
        "instruction_pdf": str(PDF_PATH),
    }
    (DELIVERY / "drive_upload_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    build_delivery_folder()
    build_pdf()
    if "--upload" in sys.argv:
        print(json.dumps(upload_to_drive(), indent=2))
    else:
        print(json.dumps({"local_delivery_folder": str(DELIVERY), "instruction_pdf": str(PDF_PATH)}, indent=2))
