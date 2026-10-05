from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = "Football YouTube Automation Playbook.pdf"


PAGE_W, PAGE_H = A4
MARGIN_X = 18 * mm
MARGIN_TOP = 18 * mm
MARGIN_BOTTOM = 17 * mm


NAVY = colors.HexColor("#111827")
INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#64748b")
LIGHT = colors.HexColor("#f3f6fb")
LINE = colors.HexColor("#d8dee9")
GREEN = colors.HexColor("#14b86a")
TEAL = colors.HexColor("#00a6a6")
YELLOW = colors.HexColor("#f2b705")
RED = colors.HexColor("#e84a5f")
BLUE = colors.HexColor("#2563eb")
PURPLE = colors.HexColor("#7c3aed")
WHITE = colors.white


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=31,
            leading=35,
            textColor=WHITE,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12.5,
            leading=18,
            textColor=colors.HexColor("#dbeafe"),
            spaceAfter=12,
        ),
        "H1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=9,
        ),
        "H2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13.5,
            leading=17,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=13.5,
            textColor=INK,
            spaceAfter=6,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.3,
            leading=11,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "CardTitle": ParagraphStyle(
            "CardTitle",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.8,
            leading=13,
            textColor=NAVY,
            spaceAfter=3,
        ),
        "CardBody": ParagraphStyle(
            "CardBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.9,
            leading=12,
            textColor=INK,
        ),
        "Kicker": ParagraphStyle(
            "Kicker",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=GREEN,
            spaceAfter=4,
        ),
        "Center": ParagraphStyle(
            "Center",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=INK,
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.6,
            leading=10,
            textColor=WHITE,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.2,
            textColor=INK,
        ),
    }
    return styles


STYLES = make_styles()


def P(text, style="Body"):
    return Paragraph(text, STYLES[style])


def bullet_list(items):
    return ListFlowable(
        [ListItem(P(item, "Body"), leftIndent=8) for item in items],
        bulletType="bullet",
        leftIndent=16,
        bulletFontName="Helvetica-Bold",
        bulletFontSize=6,
        bulletColor=GREEN,
    )


class SectionHeader(Flowable):
    def __init__(self, title, color=GREEN, width=None):
        super().__init__()
        self.title = title
        self.color = color
        self.width = width or (PAGE_W - (2 * MARGIN_X))
        self.height = 34

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(LIGHT)
        c.roundRect(0, 0, self.width, self.height, 7, stroke=0, fill=1)
        c.setFillColor(self.color)
        c.roundRect(0, 0, 6, self.height, 3, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(13, 12, self.title)


class StepCard(Flowable):
    def __init__(self, number, title, body, color=GREEN, width=None):
        super().__init__()
        self.number = number
        self.title = title
        self.body = body
        self.color = color
        self.width = width
        self.height = 84

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        c = self.canv
        w = self.width
        c.setFillColor(WHITE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, w, self.height, 7, stroke=1, fill=1)
        c.setFillColor(self.color)
        c.roundRect(10, self.height - 38, 28, 28, 14, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(24, self.height - 28, str(self.number))
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(47, self.height - 24, self.title)
        text = c.beginText(47, self.height - 43)
        text.setFont("Helvetica", 8.4)
        text.setFillColor(INK)
        max_chars = 84
        words = self.body.split()
        lines = []
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if len(candidate) > max_chars:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        for line in lines[:4]:
            text.textLine(line)
        c.drawText(text)


class PipelineDiagram(Flowable):
    def __init__(self, width=None):
        super().__init__()
        self.width = width or (PAGE_W - 2 * MARGIN_X)
        self.height = 450

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw_box(self, c, x, y, w, h, title, subtitle, color):
        c.setFillColor(WHITE)
        c.setStrokeColor(LINE)
        c.roundRect(x, y, w, h, 8, stroke=1, fill=1)
        c.setFillColor(color)
        c.roundRect(x, y + h - 10, w, 10, 5, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(x + 10, y + h - 27, title)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        text = c.beginText(x + 10, y + h - 43)
        for line in self.wrap_text(subtitle, 32)[:3]:
            text.textLine(line)
        c.drawText(text)

    def wrap_text(self, s, max_chars):
        words = s.split()
        lines = []
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if len(candidate) > max_chars:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        return lines

    def arrow(self, c, x1, y1, x2, y2):
        c.setStrokeColor(MUTED)
        c.setLineWidth(1.2)
        c.line(x1, y1, x2, y2)
        if x2 >= x1:
            c.line(x2, y2, x2 - 6, y2 + 3)
            c.line(x2, y2, x2 - 6, y2 - 3)
        else:
            c.line(x2, y2, x2 + 6, y2 + 3)
            c.line(x2, y2, x2 + 6, y2 - 3)

    def draw(self):
        c = self.canv
        w = self.width
        c.setFillColor(LIGHT)
        c.roundRect(0, 0, w, self.height, 10, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(18, self.height - 35, "End-to-End Agent Workflow")
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.8)
        c.drawString(18, self.height - 51, "A repeatable loop for creating football videos with minimal manual work.")

        cols = 3
        bw = (w - 72) / cols
        bh = 78
        xs = [24, 36 + bw, 48 + 2 * bw]
        ys = [self.height - 155, self.height - 260, self.height - 365]
        boxes = [
            ("1. Trend Radar", "Track competitors, fixtures, transfers, World Cup narratives, and rising searches.", BLUE),
            ("2. Idea Validation", "Choose topics with urgency, emotional tension, available clips, and thumbnail clarity.", GREEN),
            ("3. Script + Thesis", "Write a strong argument, retention hooks, narration, and key claims.", PURPLE),
            ("4. Clip Map", "Convert the script into exact clip needs, quote targets, timestamps, and backups.", TEAL),
            ("5. Clip Collection", "Find, download, label, and organize usable footage, interviews, photos, and graphics.", YELLOW),
            ("6. Voice + Edit Brief", "Generate voiceover and produce an editor-ready timeline with pacing notes.", RED),
            ("7. Thumbnail + Title", "Create clickable packaging, title tests, thumbnail concepts, and A/B options.", BLUE),
            ("8. Upload Package", "Prepare description, tags, chapters, pinned comment, Shorts, and metadata.", GREEN),
            ("9. Review Loop", "Check retention risks, copyright exposure, claims accuracy, and next video ideas.", PURPLE),
        ]
        positions = []
        for i, box in enumerate(boxes):
            row, col = divmod(i, cols)
            x = xs[col]
            y = ys[row]
            self.draw_box(c, x, y, bw, bh, *box)
            positions.append((x, y, bw, bh))
        for i in range(8):
            x, y, bw0, bh0 = positions[i]
            nx, ny, nbw, nbh = positions[i + 1]
            if (i + 1) % 3 != 0:
                self.arrow(c, x + bw0 + 3, y + bh0 / 2, nx - 4, ny + nbh / 2)
            else:
                self.arrow(c, x + bw0 / 2, y - 6, nx + nbw / 2, ny + nbh + 6)

        c.setStrokeColor(GREEN)
        c.setLineWidth(1.4)
        c.roundRect(18, 18, w - 36, 45, 8, stroke=1, fill=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(32, 46, "Operating rule")
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.2)
        c.drawString(32, 31, "The agent does the research, drafting, mapping, sourcing, packaging, and QA.")
        c.drawString(32, 20, "The creator approves direction, voice, final edit choices, and publishing decisions.")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#eef2f7"))
    canvas.rect(0, 0, PAGE_W, 13 * mm, stroke=0, fill=1)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(MARGIN_X, 6 * mm, "Football YouTube Automation Playbook")
    canvas.drawRightString(PAGE_W - MARGIN_X, 6 * mm, f"Page {doc.page}")
    canvas.restoreState()


def title_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#0f766e"))
    canvas.circle(PAGE_W - 40 * mm, PAGE_H - 42 * mm, 60 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#1d4ed8"))
    canvas.circle(PAGE_W - 78 * mm, PAGE_H - 12 * mm, 44 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#16a34a"))
    canvas.roundRect(MARGIN_X, PAGE_H - 96 * mm, 8 * mm, 52 * mm, 4 * mm, stroke=0, fill=1)

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 31)
    canvas.drawString(MARGIN_X + 14 * mm, PAGE_H - 50 * mm, "Football YouTube")
    canvas.drawString(MARGIN_X + 14 * mm, PAGE_H - 63 * mm, "Automation Playbook")
    canvas.setFont("Helvetica", 13)
    canvas.setFillColor(colors.HexColor("#dbeafe"))
    canvas.drawString(MARGIN_X + 14 * mm, PAGE_H - 76 * mm, "A practical agent-led workflow for football essay videos.")

    canvas.setFillColor(colors.HexColor("#172033"))
    canvas.roundRect(MARGIN_X, 58 * mm, PAGE_W - 2 * MARGIN_X, 62 * mm, 10, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(MARGIN_X + 10 * mm, 104 * mm, "What this system is designed to do")
    canvas.setFont("Helvetica", 9.5)
    lines = [
        "Turn a football topic into a ready-to-produce YouTube package.",
        "Speed up research, scriptwriting, clip hunting, voiceover, thumbnails, and upload prep.",
        "Keep the creator focused on approvals and taste instead of repetitive manual work.",
    ]
    y = 94 * mm
    for line in lines:
        canvas.setFillColor(GREEN)
        canvas.circle(MARGIN_X + 11 * mm, y + 1.5 * mm, 1.4 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#e5e7eb"))
        canvas.drawString(MARGIN_X + 16 * mm, y, line)
        y -= 9 * mm
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN_X, 27 * mm, "Prepared for: Football Channel")
    canvas.drawString(MARGIN_X, 21 * mm, "Version: Launch workflow, June 2026")
    canvas.restoreState()


def table(data, widths, header=True):
    converted = []
    for r, row in enumerate(data):
        style = "TableHead" if header and r == 0 else "TableCell"
        converted.append([P(str(cell), style) for cell in row])
    t = Table(converted, colWidths=widths, hAlign="LEFT")
    styles = [
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        styles += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ]
    for row in range(1 if header else 0, len(data)):
        if row % 2 == 0:
            styles.append(("BACKGROUND", (0, row), (-1, row), colors.HexColor("#fbfdff")))
    t.setStyle(TableStyle(styles))
    return t


def build_story():
    story = []

    story.append(SectionHeader("1. The Channel Operating Model", GREEN))
    story.append(P("The goal is to run the channel like a repeatable production system. Each video starts with a high-potential football angle, then moves through research, scripting, clip sourcing, voiceover, edit planning, thumbnail packaging, and upload prep. The agent handles the repetitive and research-heavy work. The creator approves the direction, final taste, and publishing decisions."))
    story.append(P("This model is especially useful for football essay channels because the niche depends on speed, evidence, and relevant visuals. The faster the team can turn a hot narrative into a complete production package, the more often the channel can publish while the topic is still fresh."))

    story.append(Spacer(1, 6))
    story.append(table([
        ["Role", "Main responsibility", "Typical output"],
        ["Agent", "Research topics, validate demand, draft scripts, find clip sources, create edit plans, prepare metadata.", "Video package folder with script, clip map, assets list, voiceover plan, thumbnail brief, and upload copy."],
        ["Creator", "Choose final topic, approve script direction, review sensitive claims, confirm final edit and upload.", "Taste decisions, channel voice, final go/no-go."],
        ["Editing tools", "Download permitted clips, organize files, assemble rough cut, add sound, captions, graphics, and exports.", "Final long video, Shorts, thumbnail files, and upload-ready assets."],
    ], [35 * mm, 72 * mm, 69 * mm]))

    story.append(PageBreak())

    story.append(SectionHeader("2. Step-by-Step Video Workflow", BLUE))
    steps = [
        ("Trend Radar", "Track competitor uploads, World Cup fixtures, transfer stories, player debates, and fan arguments. The agent turns this into a shortlist of video ideas ranked by urgency and upside.", BLUE),
        ("Idea Validation", "Check whether the topic has a strong thesis, emotional tension, available clips, thumbnail clarity, and a reason to watch today.", GREEN),
        ("Title and Thumbnail Direction", "Create 10 to 20 title options and 3 to 5 thumbnail concepts before writing the full script. Packaging decides whether the idea is worth producing.", PURPLE),
        ("Research Dossier", "Collect facts, quotes, timelines, statistics, match context, interviews, press conferences, and counterarguments. Each claim should have a source or a clear visual backup.", TEAL),
        ("Script Draft", "Write the narration with a strong opening claim, clear chapters, retention hooks, and a memorable ending. The agent can adjust tone from documentary to dramatic or analytical.", RED),
        ("Clip Map", "Break the script into exact visual needs. Every paragraph gets a visual instruction: quote clip, match b-roll, training footage, press photo, stat graphic, map, or backup visual.", YELLOW),
        ("Clip Collection", "Find relevant clips, download permitted material with the available tools, label every asset, record source links, timestamps, and usage notes.", GREEN),
        ("Voiceover and Edit Brief", "Generate or prepare narration, then create an editor-ready timeline with pacing notes, suggested visuals, captions, music mood, sound effects, and retention beats.", BLUE),
        ("Upload Package", "Prepare final title, description, tags, chapters, pinned comment, thumbnail brief, Shorts cutdowns, and a post-publish review checklist.", PURPLE),
    ]
    for i, (title, body, color) in enumerate(steps, 1):
        story.append(StepCard(i, title, body, color))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    story.append(SectionHeader("3. Clip Sourcing Workflow", TEAL))
    story.append(P("Clip sourcing should not start with random browsing. It should start from the script. The agent converts every script section into a clip request, then searches for the fastest legal and useful way to visualize that moment."))
    story.append(table([
        ["Clip type", "Best sources", "How the agent speeds it up"],
        ["Specific quote", "Press conferences, podcasts, Sky/TNT/talkSPORT clips, club interviews, FIFA/UEFA channels, player media days.", "Searches exact phrases, finds likely videos, records timestamps, and suggests where the quote fits in the edit."],
        ["Football b-roll", "Official club YouTube channels, training footage, tunnel cams, match previews, open training, media days, fan footage where usable.", "Builds a source list by player/team, labels footage by mood and use case, and creates backup visuals."],
        ["Match context", "Official highlights, league channels, tactical boards, photos, stats pages, lineup graphics, maps, and tables.", "Identifies the minimum footage needed and suggests transformative overlays, captions, and graphics."],
        ["Story evidence", "News reports, old interviews, manager comments, player quotes, historical clips, official announcements.", "Builds the proof chain so the video feels researched rather than generic."],
    ], [32 * mm, 68 * mm, 76 * mm]))
    story.append(Spacer(1, 8))
    story.append(P("Every clip should be stored with its source link, timestamp, purpose, and backup option. This makes the edit faster and helps avoid losing time trying to remember why an asset was downloaded."))

    story.append(P("Recommended clip map columns:", "H2"))
    story.append(table([
        ["Column", "Purpose"],
        ["Script section", "Where the visual appears in the narration."],
        ["Clip needed", "The exact person, moment, quote, match, or b-roll required."],
        ["Source link", "The original page or video where the clip came from."],
        ["Timestamp", "Start and end time for the relevant moment."],
        ["Priority", "A, B, or C depending on how essential the clip is."],
        ["Backup visual", "Still photo, stat graphic, map, quote card, or training b-roll."],
        ["Usage note", "How the editor should use it: hook, proof, transition, joke, payoff, or background."],
    ], [43 * mm, 133 * mm]))

    story.append(PageBreak())

    story.append(SectionHeader("4. The Video Package Folder", GREEN))
    story.append(P("Each video should live in its own folder. This keeps the project clean and makes it easy for the agent, editor, and creator to know what is ready, what needs approval, and what still needs sourcing."))
    story.append(table([
        ["Folder or file", "What goes inside"],
        ["01 idea brief.md", "Topic thesis, why now, target viewer, competitor proof, title options, and thumbnail direction."],
        ["02 research dossier.md", "Facts, sources, quotes, timelines, statistics, player/team context, and counterarguments."],
        ["03 script.md", "Final narration script with chapter breaks and notes for pacing."],
        ["04 clip map.csv", "Every visual needed, source links, timestamps, backup visuals, and usage notes."],
        ["05 edit brief.md", "Timeline, b-roll order, caption notes, music mood, sound design, and retention beats."],
        ["06 thumbnail title package.md", "Thumbnail concepts, title options, final description, chapters, tags, and pinned comment."],
        ["assets/raw", "Downloaded source clips, photos, audio, graphics, and references."],
        ["assets/selected", "Only the clips that make it into the edit."],
        ["exports", "Final video, Shorts, thumbnail, and upload-ready files."],
    ], [52 * mm, 124 * mm]))

    story.append(Spacer(1, 8))
    story.append(SectionHeader("5. Quality and Safety Checks", RED))
    story.append(P("Because football content often uses broadcast footage, interviews, and third-party media, the workflow should include a simple review step before publishing. The point is not to slow the channel down. It is to prevent avoidable copyright, misinformation, or quality problems."))
    story.append(bullet_list([
        "Use clips to support commentary, analysis, criticism, news reporting, or explanation rather than as filler.",
        "Keep match footage short, transformed, and surrounded by original narration, graphics, captions, or analysis.",
        "Prefer official training clips, press conferences, interviews, stills, and self-made graphics where possible.",
        "Record source links and timestamps for every clip so the edit remains traceable.",
        "Flag claims that need stronger sourcing before recording the final voiceover.",
        "Check title and thumbnail for accuracy. The hook should be dramatic, but not misleading.",
    ]))

    story.append(PageBreak())

    story.append(SectionHeader("6. Example: One Video From Start to Upload", YELLOW))
    story.append(P("<b>Working topic:</b> The World Cup Has A SERIOUS Norway Problem"))
    story.append(table([
        ["Stage", "Agent output", "Creator decision"],
        ["Idea", "Explains why Norway is timely: Haaland, Odegaard, World Cup danger-team angle, strong thumbnail potential.", "Approve or reject topic."],
        ["Research", "Collects group context, recent form, player roles, quotes, stats, and tactical points.", "Approve the argument and any sensitive claims."],
        ["Script", "Writes 10 to 14 minute narration with hook, chapters, evidence, twist, and final verdict.", "Approve tone and factual framing."],
        ["Clips", "Finds Haaland, Odegaard, Norway training, manager quotes, opposition visuals, maps, and backup graphics.", "Approve any must-use or avoid clips."],
        ["Edit", "Creates timeline: hook montage, quote cards, b-roll sections, stat graphics, and sound notes.", "Review rough cut."],
        ["Packaging", "Creates title options, thumbnail direction, description, chapters, tags, pinned comment, and Shorts ideas.", "Pick final title and thumbnail."],
        ["Upload", "Prepares upload checklist and metadata. With account access, the agent can help move assets toward publishing.", "Final publish approval."],
    ], [32 * mm, 91 * mm, 53 * mm]))

    story.append(Spacer(1, 10))
    story.append(P("The important idea: the creator should not have to manually search from a blank page. By the time editing begins, the project already has a script, clip map, source links, backup visuals, and a clear packaging direction."))

    story.append(PageBreak())

    story.append(SectionHeader("7. What Can Be Automated First", PURPLE))
    story.append(P("The best automation path is to start with the highest-friction tasks that do not require final creative judgment. This gives the channel speed without making the content feel generic."))
    story.append(table([
        ["Automation level", "Tasks"],
        ["Immediate", "Competitor tracking, topic shortlist, title generation, script drafting, clip search queries, source logging, edit briefs, upload copy."],
        ["Next", "Semi-automated clip downloading, asset naming, voiceover generation, rough timeline creation, thumbnail draft generation, Shorts selection."],
        ["Later", "Full upload preparation, recurring trend monitors, automated competitor reports, performance feedback loop, title/thumbnail testing library."],
    ], [42 * mm, 134 * mm]))

    story.append(Spacer(1, 8))
    story.append(P("The long-term system should learn from each upload. After a video is published, the agent reviews views, retention clues, click-through signals, comments, and competitor reactions, then recommends the next 5 to 10 videos."))

    story.append(PageBreak())

    story.append(PipelineDiagram())

    return story


def build_pdf():
    doc = BaseDocTemplate(
        OUTPUT,
        pagesize=A4,
        rightMargin=MARGIN_X,
        leftMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Football YouTube Automation Playbook",
        author="Codex",
    )
    frame = Frame(
        MARGIN_X,
        MARGIN_BOTTOM,
        PAGE_W - 2 * MARGIN_X,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="normal",
    )
    doc.addPageTemplates([
        PageTemplate(id="Title", frames=[frame], onPage=title_page),
        PageTemplate(id="Body", frames=[frame], onPage=footer),
    ])

    story = [NextPageTemplate("Body"), PageBreak()]
    story += build_story()
    doc.build(story)


if __name__ == "__main__":
    build_pdf()
