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
PROJECT = ROOT / "Video 004 - Pep Guardiola Warned Us About Lamine Yamal"
DELIVERY = ROOT / "Editor Deliveries" / "Pep Guardiola Tried To Warn Us About Lamine Yamal - Editor Package"
PDF_PATH = DELIVERY / "00 Instructions" / "Editor Instructions - Lamine Yamal Pep Warning.pdf"


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_files(src: Path, dst: Path, patterns: tuple[str, ...]) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for path in sorted(src.glob(pattern)):
            if path.is_file():
                copy_file(path, dst / path.name)


def build_delivery_folder() -> None:
    if DELIVERY.exists():
        shutil.rmtree(DELIVERY)
    DELIVERY.mkdir(parents=True, exist_ok=True)
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
        "08 voiceover log.md",
    ]:
        copy_file(PROJECT / rel, backups / Path(rel).name)


def para(text: str, style):
    return Paragraph(text.replace("&", "&amp;"), style)


def make_table(rows, widths, styles, small=False):
    body = styles["Small"] if small else styles["Tight"]
    table = Table([[para(str(cell), body) for cell in row] for row in rows], colWidths=widths, repeatRows=1)
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
        para("Editor Instructions: Pep Guardiola Tried To Warn Us About Lamine Yamal", styles["TitleClean"]),
        para("CapCut assembly guide for the Lamine Yamal / Pep Guardiola warning video.", styles["BodyText"]),
        Spacer(1, 0.12 * inch),
    ]
    story.append(para("1. Folder Map", styles["Section"]))
    story.append(make_table([
        ["Folder", "Purpose"],
        ["01 Voiceover", "Main ElevenLabs V3 narration. Use the 11:56 editor version."],
        ["02 Narrative Insert Clips", "Cutaways where voiceover should pause or dip and clip audio should play."],
        ["03 B-Roll Short Clips", "Muted short clips for fast visual pacing."],
        ["04 Longer B-Roll Source Clips", "Backup source clips if more visual coverage is needed."],
        ["05 Graphics", "Timeline, pressure map, and use-vs-depend graphic cards."],
        ["06 Thumbnail Options", "Three thumbnail drafts. Recommended: thumbnail_v1_he_knew.png."],
    ], [1.75 * inch, 5.85 * inch], styles))
    story.append(para("2. Main Edit Rules", styles["Section"]))
    story.append(make_table([
        ["Rule", "Instruction"],
        ["First minute", "Must include the Pep insert around 00:42-00:58 for retention."],
        ["No FIFA clips", "Avoid FIFA material because previous uploads triggered restrictions."],
        ["Pacing", "Change visuals every sentence or two. Most B-roll should last 2-6 seconds."],
        ["Tone", "Protective warning, not an anti-Lamine video."],
        ["Graphics", "Use each graphic for 5-8 seconds with a subtle zoom."],
    ], [1.55 * inch, 6.05 * inch], styles))
    story.append(para("3. Timeline Guide", styles["Section"]))
    story.append(make_table([
        ["Time", "Voiceover Section", "Visual Plan"],
        ["00:00-00:42", "Dangerous hype, Spain/Barcelona stakes, Messi question.", "Fast B-roll 001, 005, 012, 020. Text flashes: THE NEXT MESSI? / TOO SOON?"],
        ["00:42-00:58", "Pep warning setup.", "Insert: pep_warning_messi_comparison_01m28s-01m46s.mp4. Mandatory retention insert."],
        ["00:58-02:15", "Pressure wearing a crown.", "B-roll 021, 019, 017. Add graphic_lamine_timeline.png."],
        ["02:15-02:45", "Chosen-one language.", "Insert: henry_micah_chosen_one_00m02s-00m13s.mp4."],
        ["02:45-04:20", "Messi comparison trap.", "B-roll 006, 003, 004. Insert 60 Minutes Messi heir clip."],
        ["04:20-06:10", "Barcelona dependence and overuse.", "B-roll 018, 002, 007. Add graphic_pressure_map.png."],
        ["06:10-06:40", "Talent arrives faster than a career.", "Insert: sixty_minutes_age_16_spain_00m56s-01m10s.mp4."],
        ["08:35-09:00", "World Cup pressure.", "Insert: lamine_world_cup_quote_00m00s-00m15s.mp4."],
        ["09:00-10:30", "Spain solution: support, not dependence.", "B-roll 013, 014, 015, 016. Add graphic_use_vs_depend.png."],
        ["10:30-end", "Final warning: let him become Lamine.", "B-roll 009, 010, 022. End on NOT THE NEXT MESSI / THE FIRST LAMINE."],
    ], [0.9 * inch, 2.4 * inch, 4.3 * inch], styles, small=True))
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
    manifest = {"drive_folder": root, "uploaded_file_count": len(uploaded), "local_delivery_folder": str(DELIVERY), "instruction_pdf": str(PDF_PATH)}
    (DELIVERY / "drive_upload_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    build_delivery_folder()
    build_pdf()
    if "--upload" in sys.argv:
        print(json.dumps(upload_to_drive(), indent=2))
    else:
        print(json.dumps({"local_delivery_folder": str(DELIVERY), "instruction_pdf": str(PDF_PATH)}, indent=2))
