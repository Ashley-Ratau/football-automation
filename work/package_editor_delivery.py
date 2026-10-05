from __future__ import annotations

import argparse
import json
import mimetypes
import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "Video 002 - Norway Problem Short Rebuild"
DELIVERY_ROOT = ROOT / "Editor Deliveries"
DELIVERY = DELIVERY_ROOT / "The World Cup Has A SERIOUS Norway Problem - Editor Package"
PDF_PATH = DELIVERY / "00 Instructions" / "Editor Instructions - Norway Problem.pdf"


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree_files(src: Path, dst: Path, patterns: tuple[str, ...] = ("*",)) -> None:
    for pattern in patterns:
        for path in src.glob(pattern):
            if path.is_file():
                copy_file(path, dst / path.name)


def clean_delivery() -> None:
    if DELIVERY.exists():
        shutil.rmtree(DELIVERY)
    DELIVERY.mkdir(parents=True, exist_ok=True)


def build_delivery_folder() -> None:
    clean_delivery()

    copy_tree_files(
        PROJECT / "assets" / "voiceover" / "elevenlabs",
        DELIVERY / "01 Voiceover",
        ("*.mp3", "*.txt", "*.md"),
    )
    copy_tree_files(
        PROJECT / "assets" / "editor_package" / "narrative_inserts",
        DELIVERY / "02 Narrative Insert Clips",
        ("*.mp4",),
    )
    copy_tree_files(
        PROJECT / "assets" / "editor_package" / "broll_safe" / "short_clips",
        DELIVERY / "03 B-Roll Short Clips",
        ("*.mp4", "*.md"),
    )
    copy_tree_files(
        PROJECT / "assets" / "editor_package" / "broll_safe",
        DELIVERY / "04 Longer B-Roll Source Clips",
        ("*.mp4", "*.md"),
    )
    copy_tree_files(
        PROJECT / "assets" / "editor_package" / "graphics",
        DELIVERY / "05 Graphics",
        ("*.png", "*.md"),
    )
    guide_dst = DELIVERY / "00 Instructions" / "Markdown Backups"
    for rel in [
        "CapCut Workflow/EDITOR_HANDOFF.md",
        "CapCut Workflow/07 Edit Guides/CAPCUT_TIMESTAMP_EDIT_GUIDE.md",
        "CapCut Workflow/07 Edit Guides/CAPCUT_IMPORT_CHECKLIST.md",
        "03 script.md",
    ]:
        copy_file(PROJECT / rel, guide_dst / Path(rel).name)


def p(text: str, style):
    return Paragraph(text.replace("&", "&amp;"), style)


def build_pdf() -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Tight", parent=styles["BodyText"], fontSize=9, leading=11))
    styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=20, leading=24, textColor=colors.black))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=10, textColor=colors.black))

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(letter),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )

    story = []
    story.append(p("Editor Instructions: The World Cup Has A SERIOUS Norway Problem", styles["Title2"]))
    story.append(p("Simple CapCut assembly guide for the Norway video package.", styles["BodyText"]))
    story.append(Spacer(1, 0.12 * inch))

    folder_rows = [
        ["Folder", "What to use it for"],
        ["01 Voiceover", "Main ElevenLabs narration. Put voiceover_elevenlabs_full.mp3 on the main audio track."],
        ["02 Narrative Insert Clips", "Clips that interrupt the voiceover briefly: ESPN insert and San Siro proof moments."],
        ["03 B-Roll Short Clips", "Main muted clips for fast pacing. Use these under the voiceover."],
        ["04 Longer B-Roll Source Clips", "Longer backup B-roll if the editor needs extra material."],
        ["05 Graphics", "Stat, group, and weapon-stack graphics."],
    ]
    story.append(p("1. Folder Map", styles["Section"]))
    story.append(make_table(folder_rows, [2.2 * inch, 7.6 * inch], styles))

    story.append(p("2. Main Edit Rules", styles["Section"]))
    rules = [
        ["Rule", "Instruction"],
        ["Voiceover", "Use the ElevenLabs voiceover as the spine of the edit."],
        ["B-roll", "Change visuals often, usually every sentence. Most B-roll should be 2-7 seconds."],
        ["Narrative inserts", "Pause or heavily lower the voiceover, let the insert audio play, then return to narration."],
        ["Copyright caution", "Do not use old FIFA-linked clips from Video 001. Use the provided replacements and graphics."],
        ["Runtime", "Base voiceover is about 4:37. Inserts can extend slightly if pacing remains tight."],
    ]
    story.append(make_table(rules, [2.0 * inch, 7.8 * inch], styles))

    story.append(PageBreak())
    story.append(p("3. Timestamp Edit Guide", styles["Section"]))
    timeline = [
        ["Time", "Voiceover cue", "Visuals to use", "Notes"],
        ["00:00-00:09", "Norway are not a cute underdog story / warning.", "001, 002 + title text", "Open immediately. Add big text: NORWAY WARNING."],
        ["00:09-00:32", "People see one thing first: Erling Haaland.", "003, 004, 007", "Energetic Haaland intro."],
        ["00:32-00:44", "Haaland is no longer carrying a bad team.", "ESPN insert", "Use strongest 8-12 seconds. Keep insert audio. Label ESPN UK."],
        ["00:44-01:20", "Old Norway problem / version is gone / qualifying dominance.", "009, 018, 008, qualifying graphic", "Do not use 1998 FIFA footage. Use graphics instead."],
        ["01:20-01:39", "Eight wins, 37 goals, 5 conceded / San Siro setup.", "qualifying graphic, 011, 013", "One stat per beat."],
        ["01:39-02:38", "San Siro proof sequence.", "Italy opener, Nusa, Haaland 1, Haaland 2, Strand Larsen, final score", "These are narrative proof clips. Keep them short and punchy."],
        ["02:38-03:04", "Not just Haaland / Nusa, Odegaard, Haaland, Strand Larsen.", "weapon stack graphic, 023, 019, 007, 020", "Cut to each player as named."],
        ["03:04-03:39", "How Haaland changes the pitch / Odegaard control.", "020, 018, 019", "Add simple text: HIGH LINE, LOW BLOCK, DOUBLE HAALAND."],
        ["03:39-04:07", "Norway have layers: Sorloth, Nusa, Strand Larsen, Bobb.", "021, 022, 023, 024, 025, 026", "Fast player-specific cuts."],
        ["04:07-04:34", "Direct, physical, Group I, Iraq, Senegal, France.", "010, group graphic, 027, 028, 014, 016", "Use Iraq clips as safe replacement. Add FINAL BOSS for France."],
        ["04:34-end", "Built to ruin somebody else's World Cup.", "008 or final thumbnail-style frame", "End with bold text: BUILT TO RUIN SOMEBODY ELSE'S WORLD CUP."],
    ]
    story.append(make_table(timeline, [0.85 * inch, 2.7 * inch, 3.15 * inch, 3.1 * inch], styles, small=True))

    story.append(PageBreak())
    story.append(p("4. Narrative Insert Placement", styles["Section"]))
    inserts = [
        ["Insert clip", "Where it goes", "How to use it"],
        ["external_espn_norway_new_generation_03m23s-03m49s.mp4", "Around 00:32-00:44", "Use only 8-12 seconds. This is the first retention break."],
        ["italy_opener_00m20s-00m32s.mp4", "Around 01:39", "Shows Italy scoring first."],
        ["nusa_equalizer_01m08s-01m16s.mp4", "Around 02:02", "Shows the comeback starting."],
        ["haaland_goal_1_01m24s-01m36s.mp4", "Around 02:09", "First Haaland payoff."],
        ["haaland_goal_2_01m37s-01m49s.mp4", "Around 02:16", "Second Haaland payoff."],
        ["strand_larsen_final_01m49s-02m00s.mp4", "Around 02:23", "Completes the San Siro proof."],
        ["final_score_reaction_01m58s-02m06s.mp4", "Around 02:31", "Let Italy 1, Norway 4 breathe."],
    ]
    story.append(make_table(inserts, [3.8 * inch, 1.4 * inch, 4.6 * inch], styles, small=True))

    story.append(p("5. Export", styles["Section"]))
    export_rows = [
        ["Setting", "Value"],
        ["Format", "MP4"],
        ["Resolution", "1920x1080"],
        ["FPS", "30 or source default"],
        ["Filename", "norway_problem_final_capcut_export.mp4"],
        ["Save location", "final video/capcut export/"],
    ]
    story.append(make_table(export_rows, [2.1 * inch, 7.7 * inch], styles))

    doc.build(story)


def make_table(rows, widths, styles, small: bool = False):
    data = []
    style = styles["Small"] if small else styles["Tight"]
    for row in rows:
        data.append([p(str(cell), style) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def upload_to_drive(make_shareable: bool) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "work"))
    from youtube_oauth_tool import drive_service

    service = drive_service()

    def create_folder(name: str, parent_id: str | None = None) -> dict:
        metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            metadata["parents"] = [parent_id]
        return service.files().create(body=metadata, fields="id,name,webViewLink").execute()

    def upload_file(path: Path, parent_id: str) -> dict:
        from googleapiclient.http import MediaFileUpload

        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        metadata = {"name": path.name, "parents": [parent_id]}
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=True)
        return service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name,mimeType,webViewLink",
        ).execute()

    root_folder = create_folder(DELIVERY.name)
    folder_ids = {DELIVERY: root_folder["id"]}
    uploaded = []

    for folder in sorted([p for p in DELIVERY.rglob("*") if p.is_dir()]):
        parent = folder.parent
        folder_ids[folder] = create_folder(folder.name, folder_ids[parent])["id"]

    for file_path in sorted([p for p in DELIVERY.rglob("*") if p.is_file()]):
        uploaded.append(upload_file(file_path, folder_ids[file_path.parent]))

    if make_shareable:
        service.permissions().create(
            fileId=root_folder["id"],
            body={"type": "anyone", "role": "reader"},
            fields="id",
        ).execute()

    manifest = {
        "drive_folder": root_folder,
        "shareable": make_shareable,
        "uploaded_file_count": len(uploaded),
        "local_delivery_folder": str(DELIVERY),
        "instruction_pdf": str(PDF_PATH),
    }
    (DELIVERY / "drive_upload_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--shareable", action="store_true")
    args = parser.parse_args()

    build_delivery_folder()
    build_pdf()

    if args.upload:
        manifest = upload_to_drive(args.shareable)
        print(json.dumps(manifest, indent=2))
    else:
        print(json.dumps({"local_delivery_folder": str(DELIVERY), "instruction_pdf": str(PDF_PATH)}, indent=2))


if __name__ == "__main__":
    main()
