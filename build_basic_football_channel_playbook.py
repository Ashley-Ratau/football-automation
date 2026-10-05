from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)


OUTPUT = "Football YouTube Automation Playbook - Basic.pdf"


def styles():
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=18,
        ),
        "H1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.black,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "H2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.black,
            spaceAfter=7,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.black,
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.black,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.black,
        ),
    }


S = styles()


def p(text, style="Body"):
    return Paragraph(text, S[style])


def bullets(items):
    return ListFlowable(
        [ListItem(p(item), leftIndent=8) for item in items],
        bulletType="bullet",
        leftIndent=16,
    )


def make_table(rows, widths):
    table_rows = []
    for i, row in enumerate(rows):
        style = "TableHead" if i == 0 else "TableCell"
        table_rows.append([p(str(cell), style) for cell in row])
    t = Table(table_rows, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.black)
    canvas.drawString(18 * mm, 10 * mm, "Football YouTube Automation Playbook")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def workflow_diagram():
    rows = [
        ["Step", "Agent work", "Creator decision"],
        ["1. Trend Radar", "Monitor competitors, fixtures, transfers, player debates, and fast-moving football narratives.", "Choose whether the topic fits the channel."],
        ["2. Idea Validation", "Check urgency, emotional hook, clip availability, title potential, and thumbnail strength.", "Approve the video angle."],
        ["3. Research Dossier", "Collect sources, quotes, statistics, match context, interviews, and counterarguments.", "Approve the thesis and sensitive claims."],
        ["4. Script", "Write the full narration with hook, chapters, retention beats, and final payoff.", "Approve voice, tone, and structure."],
        ["5. Clip Map", "Turn every script section into a visual request with source links, timestamps, and backups.", "Mark must-use and avoid clips."],
        ["6. Clip Collection", "Find and download relevant clips using available tools, then label and organize assets.", "Review key assets if needed."],
        ["7. Voice and Edit Brief", "Prepare voiceover and an editor-ready timeline with b-roll, captions, graphics, and sound notes.", "Approve rough cut direction."],
        ["8. Thumbnail and Title", "Create title options, thumbnail concepts, description, tags, chapters, and pinned comment.", "Pick final packaging."],
        ["9. Upload and Review", "Prepare the upload package and review performance after publishing.", "Approve publish and next-video direction."],
    ]
    return make_table(rows, [27 * mm, 83 * mm, 58 * mm])


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Football YouTube Automation Playbook - Basic",
        author="Codex",
    )

    story = []
    story.append(p("Football YouTube Automation Playbook", "Title"))
    story.append(p("A practical agent-led workflow for creating football essay videos with less manual work.", "Subtitle"))

    story.append(p("1. The Channel Operating Model", "H1"))
    story.append(p("The channel should run like a repeatable production system. Each video starts with a high-potential football angle, then moves through research, scripting, clip sourcing, voiceover, edit planning, thumbnail packaging, and upload preparation."))
    story.append(p("The agent handles the repetitive and research-heavy work. The creator stays focused on approvals, taste, final judgment, and publishing decisions."))
    story.append(
        make_table(
            [
                ["Role", "Main responsibility", "Typical output"],
                ["Agent", "Research topics, validate demand, draft scripts, find clips, create edit plans, and prepare metadata.", "A complete video package with script, clip map, source links, edit brief, thumbnail direction, and upload copy."],
                ["Creator", "Approve topic, script direction, sensitive claims, final edit, title, thumbnail, and upload.", "Taste decisions and final go/no-go."],
                ["Editing tools", "Download permitted clips, organize files, assemble rough cut, add sound, captions, graphics, and exports.", "Final long video, Shorts, thumbnail, and upload-ready files."],
            ],
            [31 * mm, 68 * mm, 69 * mm],
        )
    )

    story.append(PageBreak())
    story.append(p("2. Step-by-Step Workflow", "H1"))
    steps = [
        ("Trend Radar", "Track competitor uploads, World Cup fixtures, transfers, player debates, fan arguments, and rising searches. The agent turns this into a ranked shortlist of video ideas."),
        ("Idea Validation", "Check whether the topic has urgency, emotional tension, a clear thesis, available clips, and a thumbnail that can be understood instantly."),
        ("Title and Thumbnail Direction", "Create title options and thumbnail concepts before writing the full script. If the video cannot be packaged clearly, it should not be produced yet."),
        ("Research Dossier", "Collect facts, timelines, stats, quotes, interviews, press conferences, and counterarguments. Every major claim should have a source or clear evidence path."),
        ("Script Draft", "Write the narration with a strong opening claim, clear chapters, retention hooks, and a memorable ending. The script can be dramatic, analytical, documentary-style, or punchier depending on the channel voice."),
        ("Clip Map", "Break the script into exact visual needs. Every paragraph gets a visual instruction: quote clip, match b-roll, training footage, press photo, stat graphic, map, or backup visual."),
        ("Clip Collection", "Find relevant clips, download permitted material with the available tools, label every asset, and record source links, timestamps, priority, and usage notes."),
        ("Voiceover and Edit Brief", "Generate or prepare the narration, then create an editor-ready timeline with pacing notes, suggested visuals, captions, music mood, sound effects, and retention beats."),
        ("Upload Package", "Prepare final title, description, tags, chapters, pinned comment, thumbnail notes, Shorts cutdowns, and a post-publish review checklist."),
    ]
    for i, (title, body) in enumerate(steps, 1):
        story.append(p(f"{i}. {title}", "H2"))
        story.append(p(body))

    story.append(PageBreak())
    story.append(p("3. Clip Sourcing Workflow", "H1"))
    story.append(p("Clip sourcing should start from the script, not from random browsing. The agent converts each script section into a precise clip request, then searches for the fastest useful way to visualize that moment."))
    story.append(
        make_table(
            [
                ["Clip type", "Best sources", "How the agent speeds it up"],
                ["Specific quote", "Press conferences, podcasts, Sky/TNT/talkSPORT clips, club interviews, FIFA/UEFA channels, and player media days.", "Searches exact phrases, finds likely videos, records timestamps, and suggests how the quote fits the edit."],
                ["Football b-roll", "Official club channels, training footage, tunnel cams, open training, media days, and usable fan footage.", "Builds source lists by player/team, labels footage by mood and use case, and creates backup visuals."],
                ["Match context", "Official highlights, league channels, tactical boards, photos, stats pages, lineup graphics, maps, and tables.", "Identifies the minimum footage needed and suggests transformative overlays, captions, and graphics."],
                ["Story evidence", "News reports, old interviews, manager comments, player quotes, historical clips, and official announcements.", "Builds the proof chain so the video feels researched rather than generic."],
            ],
            [30 * mm, 67 * mm, 71 * mm],
        )
    )
    story.append(p("Recommended clip map columns", "H2"))
    story.append(
        bullets(
            [
                "Script section: where the visual appears in the narration.",
                "Clip needed: the exact person, moment, quote, match, or b-roll required.",
                "Source link: the original page or video where the clip came from.",
                "Timestamp: start and end time for the relevant moment.",
                "Priority: A, B, or C depending on how essential the clip is.",
                "Backup visual: still photo, stat graphic, map, quote card, or training b-roll.",
                "Usage note: how the editor should use it: hook, proof, transition, joke, payoff, or background.",
            ]
        )
    )

    story.append(PageBreak())
    story.append(p("4. Video Package Folder", "H1"))
    story.append(p("Each video should live in its own folder. This keeps the project clean and makes it easy to know what is ready, what needs approval, and what still needs sourcing."))
    story.append(
        make_table(
            [
                ["Folder or file", "What goes inside"],
                ["01 idea brief.md", "Topic thesis, why now, target viewer, competitor proof, title options, and thumbnail direction."],
                ["02 research dossier.md", "Facts, sources, quotes, timelines, statistics, player/team context, and counterarguments."],
                ["03 script.md", "Final narration script with chapter breaks and pacing notes."],
                ["04 clip map.csv", "Every visual needed, source links, timestamps, backup visuals, and usage notes."],
                ["05 edit brief.md", "Timeline, b-roll order, caption notes, music mood, sound design, and retention beats."],
                ["06 thumbnail title package.md", "Thumbnail concepts, title options, final description, chapters, tags, and pinned comment."],
                ["assets/raw", "Downloaded source clips, photos, audio, graphics, and references."],
                ["assets/selected", "Only the clips that make it into the edit."],
                ["exports", "Final video, Shorts, thumbnail, and upload-ready files."],
            ],
            [50 * mm, 118 * mm],
        )
    )

    story.append(p("5. Quality and Safety Checks", "H1"))
    story.append(p("Football content often uses broadcast footage, interviews, and third-party media. The workflow should include a simple review step before publishing to reduce copyright, misinformation, and quality issues."))
    story.append(
        bullets(
            [
                "Use clips to support commentary, analysis, criticism, news reporting, or explanation rather than as filler.",
                "Keep match footage short, transformed, and surrounded by original narration, graphics, captions, or analysis.",
                "Prefer official training clips, press conferences, interviews, stills, and self-made graphics where possible.",
                "Record source links and timestamps for every clip so the edit remains traceable.",
                "Flag claims that need stronger sourcing before recording the final voiceover.",
                "Keep titles and thumbnails dramatic but accurate.",
            ]
        )
    )

    story.append(PageBreak())
    story.append(p("6. Example Video Workflow", "H1"))
    story.append(p("Working topic: The World Cup Has A SERIOUS Norway Problem", "H2"))
    story.append(
        make_table(
            [
                ["Stage", "Agent output", "Creator decision"],
                ["Idea", "Explains why Norway is timely: Haaland, Odegaard, World Cup danger-team angle, and strong thumbnail potential.", "Approve or reject topic."],
                ["Research", "Collects group context, recent form, player roles, quotes, stats, and tactical points.", "Approve argument and sensitive claims."],
                ["Script", "Writes 10 to 14 minute narration with hook, chapters, evidence, twist, and final verdict.", "Approve tone and factual framing."],
                ["Clips", "Finds Haaland, Odegaard, Norway training, manager quotes, opposition visuals, maps, and backup graphics.", "Approve must-use or avoid clips."],
                ["Edit", "Creates timeline: hook montage, quote cards, b-roll sections, stat graphics, and sound notes.", "Review rough cut."],
                ["Packaging", "Creates title options, thumbnail direction, description, chapters, tags, pinned comment, and Shorts ideas.", "Pick final title and thumbnail."],
                ["Upload", "Prepares upload checklist and metadata. With account access, the agent can help move assets toward publishing.", "Final publish approval."],
            ],
            [28 * mm, 90 * mm, 50 * mm],
        )
    )

    story.append(PageBreak())
    story.append(p("7. What Can Be Automated First", "H1"))
    story.append(
        make_table(
            [
                ["Automation level", "Tasks"],
                ["Immediate", "Competitor tracking, topic shortlist, title generation, script drafting, clip search queries, source logging, edit briefs, and upload copy."],
                ["Next", "Semi-automated clip downloading, asset naming, voiceover generation, rough timeline creation, thumbnail draft generation, and Shorts selection."],
                ["Later", "Full upload preparation, recurring trend monitors, automated competitor reports, performance feedback loop, and title/thumbnail testing library."],
            ],
            [42 * mm, 126 * mm],
        )
    )
    story.append(p("The long-term system should learn from each upload. After publishing, the agent reviews views, retention clues, click-through signals, comments, and competitor reactions, then recommends the next videos."))

    story.append(PageBreak())
    story.append(p("8. Workflow Diagram", "H1"))
    story.append(p("Use this as the simple operating map for every video. The process loops after publishing because each upload teaches the channel what to make next."))
    story.append(workflow_diagram())

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build()
