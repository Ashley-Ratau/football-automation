"""Animated broadcast-style graphics (RGBA) for 'The Ballon d'Or Race Isn't Even Close'.

Each graphic is a function draw(t, dur) -> PIL RGBA 1920x1080 image. Rendered to
ProRes 4444 .mov with alpha and composited over darkened footage by build.py.
"""
from pathlib import Path
import math, subprocess, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = Path(__file__).resolve().parent
FF = r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
W, H, FPS = 1920, 1080, 30
F = P/'assets'/'fonts'
GOLD = (232, 189, 82); GOLD_D = (150, 112, 36); WHITE = (245, 245, 240); GREY = (150, 150, 158)
RED = (220, 40, 60); KANE = (214, 38, 58); YAMAL = (232, 189, 82); INK = (10, 10, 14)

_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        f = ImageFont.truetype(str(F/name), size)
        if name == 'Oswald.ttf':
            try: f.set_variation_by_axes([700])
            except Exception: pass
        if name == 'Inter.ttf':
            try: f.set_variation_by_axes([32, 800])
            except Exception: pass
        _fc[k] = f
    return _fc[k]
ANTON = lambda s: font('Anton-Regular.ttf', s)
OSW = lambda s: font('Oswald.ttf', s)
INTER = lambda s: font('Inter.ttf', s)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, start, length): return clamp((t - start) / length)

def canvas(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))

def text_layer(txt, fnt, fill, alpha=1.0, tracking=0, shadow=True):
    """Render text to its own tight RGBA layer (so it can be scaled / moved)."""
    if tracking:
        widths = [fnt.getbbox(c)[2] - fnt.getbbox(c)[0] if c != ' ' else fnt.size // 3 for c in txt]
        tw = sum(widths) + tracking * (len(txt) - 1)
    else:
        b = fnt.getbbox(txt); tw = b[2] - b[0]
    asc, desc = fnt.getmetrics()
    pad = 30
    im = Image.new('RGBA', (int(tw) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def put(dd, col):
        if tracking:
            x = pad
            for c, w in zip(txt, widths):
                bb = fnt.getbbox(c)
                dd.text((x - bb[0], pad), c, font=fnt, fill=col); x += w + tracking
        else:
            dd.text((pad - fnt.getbbox(txt)[0], pad), txt, font=fnt, fill=col)
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); put(ImageDraw.Draw(sh), (0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(sh, (0, 6))
    put(d, fill + (255,))
    if alpha < 1:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im.putalpha(a)
    return im

def paste_center(base, layer, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.003: return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.LANCZOS)
    if alpha < 1:
        layer = layer.copy(); layer.putalpha(layer.getchannel('A').point(lambda v: int(v * alpha)))
    base.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))

def paste_left(base, layer, x, cy, alpha=1.0):
    paste_center(base, layer, x + layer.width / 2, cy, 1.0, alpha)

def bar(base, x, y, w, h, col, alpha=1.0):
    d = ImageDraw.Draw(base); d.rectangle([x, y, x + w, y + h], fill=col + (int(255 * alpha),))

def vignette_panel(base, alpha=0.55):
    """Soft dark band so text reads over busy footage."""
    ov = Image.new('RGBA', (W, H), (0, 0, 0, int(255 * alpha)))
    base.alpha_composite(ov)

# ---------------------------------------------------------------- graphics
def big_number(value, label, sub='', color=WHITE, count=True, accent=GOLD):
    """A huge counting number with a label under it."""
    def draw(t, dur):
        im = canvas()
        p = ease(prog(t, 0, 0.9))
        n = int(round(value * p)) if count else value
        s = back(prog(t, 0, 0.45)) * 0.35 + 0.65
        paste_center(im, text_layer(str(n), ANTON(420), color), W / 2, 470, s, ease(prog(t, 0, 0.25)))
        la = ease(prog(t, 0.35, 0.4))
        lab = text_layer(label.upper(), OSW(74), accent, tracking=6)
        paste_center(im, lab, W / 2, 780 + 30 * (1 - la), 1, la)
        bw = 520 * ease(prog(t, 0.25, 0.5)); bar(im, W / 2 - bw / 2, 720, bw, 6, accent)
        if sub:
            sa = ease(prog(t, 0.6, 0.4))
            paste_center(im, text_layer(sub, INTER(40), GREY), W / 2, 875, 1, sa)
        return im
    return draw

def stat_stack(lines, title='', accent=GOLD, color=WHITE, stagger=None, start=0.0):
    """Lines of stats that slam in one after another, left aligned on a panel."""
    def draw(t, dur):
        im = canvas()
        pw = 1100 * ease(prog(t, 0, 0.35))
        panel = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(panel)
        d.rectangle([0, 0, pw, H], fill=(8, 8, 12, 205)); im.alpha_composite(panel)
        bar(im, pw - 8, 0, 8, H, accent, 1)
        y = 200
        if title:
            paste_left(im, text_layer(title.upper(), OSW(54), accent, tracking=8), 110, 170, ease(prog(t, 0.15, 0.3)))
            y = 300
        step = stagger or max(0.35, min(1.2, (dur - 1.5) / max(1, len(lines))))
        n = len(lines); gap = min(150, (H - y - 80) / max(1, n))
        for i, ln in enumerate(lines):
            big, small = ln if isinstance(ln, tuple) else (ln, '')
            a = ease(prog(t, start + 0.3 + i * step, 0.3)); dx = -80 * (1 - a)
            row = text_layer(big, ANTON(int(gap * 0.78)), color)
            paste_left(im, row, 110 + dx, y + i * gap + gap * 0.42, a)
            if small:
                paste_left(im, text_layer(small, INTER(34), GREY), 110 + row.width - 40 + dx, y + i * gap + gap * 0.5, a)
        return im
    return draw

def versus(left, right, rows, lcol=KANE, rcol=YAMAL, highlight=None):
    """Kane vs Yamal comparison board. rows = [(label, lval, rval, winner 'l'/'r'/None)]."""
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.62 * ease(prog(t, 0, 0.3)))
        a = ease(prog(t, 0, 0.4))
        paste_center(im, text_layer(left.upper(), ANTON(110), lcol), 480 - 200 * (1 - a), 150, 1, a)
        paste_center(im, text_layer(right.upper(), ANTON(110), rcol), 1440 + 200 * (1 - a), 150, 1, a)
        paste_center(im, text_layer('VS', OSW(64), GREY), W / 2, 150, back(prog(t, 0.2, 0.4)), a)
        step = max(0.35, min(0.9, (dur - 1.2) / max(1, len(rows))))
        for i, (lab, lv, rv, win) in enumerate(rows):
            y = 320 + i * 125; r = ease(prog(t, 0.4 + i * step, 0.35))
            if r <= 0: continue
            bar(im, 160, y - 50, 1600 * r, 100, (20, 20, 26), 0.85)
            if win == 'l': bar(im, 160, y - 50, 10, 100, lcol, r)
            if win == 'r': bar(im, 1750, y - 50, 10, 100, rcol, r)
            paste_center(im, text_layer(lab.upper(), OSW(40), GREY, tracking=3), W / 2, y, 1, r)
            paste_center(im, text_layer(lv, ANTON(70), WHITE if win != 'r' else GREY), 430, y, 1, r)
            paste_center(im, text_layer(rv, ANTON(70), WHITE if win != 'l' else GREY), 1490, y, 1, r)
        return im
    return draw

def exhibit(letter, subtitle):
    """Case-file title: 'EXHIBIT A' stamped on with shake."""
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.5 * ease(prog(t, 0, 0.2)))
        p = prog(t, 0.05, 0.22); s = 1.8 - 0.8 * ease(p)
        shake = (random.Random(int(t * 30)).uniform(-8, 8) if 0.27 < t < 0.5 else 0)
        stamp = text_layer(f'EXHIBIT {letter}', ANTON(260), GOLD, tracking=10)
        paste_center(im, stamp, W / 2 + shake, 470 + shake, s, ease(prog(t, 0.05, 0.12)))
        sa = ease(prog(t, 0.55, 0.35))
        paste_center(im, text_layer(subtitle.upper(), OSW(70), WHITE, tracking=14), W / 2, 680 + 20 * (1 - sa), 1, sa)
        bw = 900 * ease(prog(t, 0.45, 0.4)); bar(im, W / 2 - bw / 2, 615, bw, 5, GOLD)
        return im
    return draw

def headline(lines, colors=None, size=150, y=None, sub='', sub_color=GREY, align_y=540):
    """Centered bold statement, word lines slam in."""
    colors = colors or [WHITE] * len(lines)
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.5 * ease(prog(t, 0, 0.25)))
        n = len(lines); total = n * size * 1.05
        y0 = align_y - total / 2 + size * 0.52
        for i, (ln, c) in enumerate(zip(lines, colors)):
            a = prog(t, 0.08 + i * 0.28, 0.3)
            paste_center(im, text_layer(ln, ANTON(size), c, tracking=2), W / 2, y0 + i * size * 1.05, 1.25 - 0.25 * back(a), ease(a))
        if sub:
            sa = ease(prog(t, 0.15 + n * 0.28, 0.4))
            paste_center(im, text_layer(sub, INTER(44), sub_color), W / 2, y0 + n * size * 1.05 + 10, 1, sa)
        return im
    return draw

def criteria():
    items = [('01', 'INDIVIDUAL PERFORMANCE'), ('02', 'COLLECTIVE PERFORMANCE & TITLES'), ('03', 'CLASS & FAIR PLAY')]
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.68 * ease(prog(t, 0, 0.3)))
        paste_center(im, text_layer('THE BALLON D\'OR CRITERIA', OSW(58), GOLD, tracking=10), W / 2, 210, 1, ease(prog(t, 0, 0.4)))
        bar(im, W / 2 - 300 * ease(prog(t, 0.2, 0.4)), 262, 600 * ease(prog(t, 0.2, 0.4)), 4, GOLD)
        step = max(0.5, min(1.4, (dur - 1.5) / 3))
        for i, (n, s) in enumerate(items):
            a = ease(prog(t, 0.4 + i * step, 0.35)); y = 430 + i * 170
            paste_left(im, text_layer(n, ANTON(130), GOLD_D), 330 - 60 * (1 - a), y, a)
            paste_left(im, text_layer(s, ANTON(92), WHITE), 520 - 60 * (1 - a), y, a)
        paste_center(im, text_layer('SOURCE: FRANCE FOOTBALL / UEFA', INTER(26), GREY), W / 2, 1000, 1, ease(prog(t, 1, 0.5)))
        return im
    return draw

def window_timeline():
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.6 * ease(prog(t, 0, 0.3)))
        paste_center(im, text_layer('THE VOTING WINDOW', OSW(58), GOLD, tracking=10), W / 2, 260, 1, ease(prog(t, 0, 0.4)))
        p = ease(prog(t, 0.3, 1.6)); x0, x1, y = 260, 1660, 560
        bar(im, x0, y - 4, (x1 - x0), 8, (60, 60, 66), 0.9)
        bar(im, x0, y - 4, (x1 - x0) * p, 8, GOLD)
        d = ImageDraw.Draw(im)
        for x, lab, sub in [(x0, '3 AUG 2025', 'SEASON BEGINS'), (x1, '19 JUL 2026', 'WORLD CUP FINAL')]:
            a = ease(prog(t, 0.2 if x == x0 else 1.6, 0.4))
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=GOLD + (int(255 * a),))
            paste_center(im, text_layer(lab, ANTON(80), WHITE), x, y - 110, 1, a)
            paste_center(im, text_layer(sub, OSW(40), GREY, tracking=4), x, y + 80, 1, a)
        return im
    return draw

def odds_board():
    rows = [('HARRY KANE', 'FAVOURITE', KANE), ('LAMINE YAMAL', '2ND', YAMAL), ('KYLIAN MBAPPÉ', '3RD', WHITE)]
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.6 * ease(prog(t, 0, 0.3)))
        paste_center(im, text_layer('BALLON D\'OR 2026 · BETTING MARKET', OSW(50), GREY, tracking=6), W / 2, 230, 1, ease(prog(t, 0, 0.3)))
        for i, (n, o, c) in enumerate(rows):
            a = ease(prog(t, 0.25 + i * 0.3, 0.3)); y = 400 + i * 165
            bar(im, 360, y - 62, 1200 * a, 124, (18, 18, 24), 0.9); bar(im, 360, y - 62, 12, 124, c, a)
            paste_left(im, text_layer(n, ANTON(90), WHITE if i else c), 410 - 40 * (1 - a), y, a)
            ol = text_layer(o, OSW(60), c if i == 0 else GREY, tracking=4); paste_left(im, ol, 1520 - ol.width, y, a)
        paste_center(im, text_layer('Oddschecker, 29 Sep 2026', INTER(26), GREY), W / 2, 930, 1, ease(prog(t, 1, 0.4)))
        return im
    return draw

def trophy_cabinet():
    names = [('YAMAL', YAMAL, [1, 1], '19'), ('KANE', KANE, [1, 0], '33'), ('DEMBÉLÉ', WHITE, [1, 0], '29'), ('MBAPPÉ', WHITE, [0, 0], '27')]
    cols = ['LEAGUE TITLE', 'WORLD CUP', 'AGE']
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.7 * ease(prog(t, 0, 0.3)))
        for j, c in enumerate(cols):
            paste_center(im, text_layer(c, OSW(42), GREY, tracking=4), 980 + j * 330, 230, 1, ease(prog(t, 0.1, 0.3)))
        d = ImageDraw.Draw(im)
        for i, (n, col, v, age) in enumerate(names):
            a = ease(prog(t, 0.3 + i * 0.35, 0.3)); y = 360 + i * 160
            paste_left(im, text_layer(n, ANTON(100), col), 280 - 50 * (1 - a), y, a)
            for j, has in enumerate(v):
                b = ease(prog(t, 0.5 + i * 0.35 + j * 0.12, 0.25)); cx = 980 + j * 330
                if has:
                    r = 42 * back(b); d.ellipse([cx - r, y - r, cx + r, y + r], fill=GOLD + (int(255 * b),))
                    paste_center(im, text_layer('✓', INTER(54), INK, shadow=False), cx, y, 1, b)
                else:
                    paste_center(im, text_layer('—', ANTON(70), (80, 80, 86)), cx, y, 1, b)
            b = ease(prog(t, 0.74 + i * 0.35, 0.25))
            paste_center(im, text_layer(age, ANTON(90), GOLD if i == 0 else WHITE), 980 + 2 * 330, y, 1, b)
        return im
    return draw

def gravity(dur_total=None):
    """Top-down tactical: three defenders drawn to Yamal, space opens for a runner."""
    def draw(t, dur):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        a0 = ease(prog(t, 0, 0.4))
        # pitch
        pitch = Image.new('RGBA', (W, H), (14, 46, 30, int(235 * a0))); pd = ImageDraw.Draw(pitch)
        for k in range(0, W, 160): pd.rectangle([k, 0, k + 80, H], fill=(16, 52, 34, int(235 * a0)))
        lc = (220, 230, 220, int(150 * a0))
        pd.rectangle([60, 60, W - 60, H - 60], outline=lc, width=4)
        pd.rectangle([W - 60 - 300, 260, W - 60, H - 260], outline=lc, width=4)
        pd.rectangle([W - 60 - 110, 400, W - 60, H - 400], outline=lc, width=4)
        pd.line([W / 2, 60, W / 2, H - 60], fill=lc, width=4); pd.ellipse([W / 2 - 150, H / 2 - 150, W / 2 + 150, H / 2 + 150], outline=lc, width=4)
        im.alpha_composite(pitch); d = ImageDraw.Draw(im)
        T = dur
        m = lambda s, l: ease(prog(t, T * s, T * l))
        yamal = (1380, 880)
        # defenders: full-back, winger, midfielder move toward yamal
        defs = [((1600, 640), (1460, 800), 0.12), ((1250, 560), (1300, 780), 0.28), ((1150, 400), (1240, 680), 0.44)]
        for k, (s, e, st) in enumerate(defs):
            p = m(st, 0.14); x = s[0] + (e[0] - s[0]) * p; y = s[1] + (e[1] - s[1]) * p
            if p > 0.05:
                d.line([s, (x, y)], fill=(230, 80, 90, int(140 * p)), width=5)
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=RED + (255,), outline=(255, 255, 255, 255), width=3)
            # attention line to yamal
            if p > 0.6:
                la = int(200 * (p - 0.6) / 0.4)
                for q in range(0, 20, 2):
                    fx = x + (yamal[0] - x) * q / 20; fy = y + (yamal[1] - y) * q / 20
                    d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=(255, 220, 120, la))
        other_def = [(1780, 330), (1720, 620), (980, 230)]
        for x, y in other_def: d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=RED + (int(255 * a0),), outline=(255, 255, 255, int(255 * a0)), width=3)
        # yamal with pulsing ring
        pr = 40 + 26 * (0.5 + 0.5 * math.sin(t * 5))
        d.ellipse([yamal[0] - pr, yamal[1] - pr, yamal[0] + pr, yamal[1] + pr], outline=GOLD + (int(170 * a0),), width=4)
        d.ellipse([yamal[0] - 28, yamal[1] - 28, yamal[0] + 28, yamal[1] + 28], fill=GOLD + (int(255 * a0),), outline=(255, 255, 255, 255), width=3)
        paste_center(im, text_layer('19', OSW(30), INK, shadow=False), yamal[0], yamal[1] - 2, 1, a0)
        paste_center(im, text_layer('YAMAL', OSW(40), GOLD, tracking=3), yamal[0], yamal[1] + 64, 1, a0)
        # free space zone + runner
        zp = m(0.6, 0.15)
        if zp > 0:
            zone = Image.new('RGBA', (W, H), (0, 0, 0, 0)); zd = ImageDraw.Draw(zone)
            zd.ellipse([1260, 170, 1640, 450], fill=(255, 215, 90, int(70 * zp)), outline=(255, 215, 90, int(220 * zp)), width=4)
            im.alpha_composite(zone); d = ImageDraw.Draw(im)
            paste_center(im, text_layer('SPACE', ANTON(70), GOLD), 1450, 250, 1, zp)
        mate = (1050, 480); rp = m(0.72, 0.18)
        rx = mate[0] + (1450 - mate[0]) * rp; ry = mate[1] + (330 - mate[1]) * rp
        if rp > 0:
            for q in range(0, 30, 3):
                fx = mate[0] + (rx - mate[0]) * q / 30; fy = mate[1] + (ry - mate[1]) * q / 30
                d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(120, 170, 255, 230))
        d.ellipse([rx - 26, ry - 26, rx + 26, ry + 26], fill=(40, 90, 200, int(255 * a0)), outline=(255, 255, 255, int(255 * a0)), width=3)
        pp = m(0.82, 0.08)
        if pp > 0:
            px = yamal[0] + (rx - yamal[0]) * pp; py = yamal[1] + (ry - yamal[1]) * pp
            d.line([yamal, (px, py)], fill=(255, 255, 255, 230), width=5)
        # counter caption
        cnt = sum(1 for (_, _, st) in defs if m(st, 0.14) > 0.6)
        if cnt:
            paste_left(im, text_layer(f'{cnt} PLAYER{"S" if cnt > 1 else ""} ON ONE TEENAGER', ANTON(64), WHITE), 110, 190, 1)
        return im
    return draw

def date_card():
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.55 * ease(prog(t, 0, 0.3)))
        a = prog(t, 0.05, 0.35)
        paste_center(im, text_layer('26 OCTOBER', ANTON(220), GOLD, tracking=4), W / 2, 450, 1.2 - 0.2 * back(a), ease(a))
        b = ease(prog(t, 0.45, 0.4))
        paste_center(im, text_layer('THE LONDON PALLADIUM', OSW(70), WHITE, tracking=14), W / 2, 640, 1, b)
        return im
    return draw

def end_card():
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.7 * ease(prog(t, 0, 0.6)))
        for i, (ln, c) in enumerate([('WHO GETS', WHITE), ('YOUR VOTE?', GOLD)]):
            a = prog(t, 0.2 + i * 0.35, 0.35)
            paste_center(im, text_layer(ln, ANTON(200), c), W / 2, 400 + i * 210, 1.2 - 0.2 * back(a), ease(a))
        paste_center(im, text_layer('TELL ME IN THE COMMENTS', OSW(56), GREY, tracking=10), W / 2, 790, 1, ease(prog(t, 1.0, 0.4)))
        return im
    return draw

def title_card():
    """The opening title slam."""
    def draw(t, dur):
        im = canvas(); vignette_panel(im, 0.45 * ease(prog(t, 0, 0.2)))
        lines = [('THE BALLON D\'OR RACE', WHITE, 120), ('ISN\'T EVEN', WHITE, 200), ('CLOSE', GOLD, 330)]
        y = [250, 450, 730]
        for i, (ln, c, s) in enumerate(lines):
            a = prog(t, 0.05 + i * 0.25, 0.25)
            shake = random.Random(int(t * 30) + i).uniform(-10, 10) if i == 2 and 0.6 < t < 0.85 else 0
            paste_center(im, text_layer(ln, ANTON(s), c, tracking=3), W / 2 + shake, y[i] + shake, 1.4 - 0.4 * ease(a), ease(a))
        return im
    return draw

def lower_third(name, role):
    im = canvas(); d = ImageDraw.Draw(im)
    nl = text_layer(name, ANTON(64), WHITE); rl = text_layer(role, INTER(32), GREY, shadow=False)
    w = max(nl.width, rl.width) + 40
    d.rectangle([70, 60, 70 + w, 200], fill=(10, 10, 14, 215)); d.rectangle([70, 60, 80, 200], fill=GOLD + (255,))
    paste_left(im, nl, 80, 100); paste_left(im, rl, 80, 162)
    return im

def render(draw, dur, out):
    out = Path(out); n = max(1, round(dur * FPS))
    cmd = [FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-frames:v', str(n), '-c:v', 'qtrle', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=open(str(out)+".log","w"))
    for i in range(n):
        p.stdin.write(draw(i / FPS, dur).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode: raise RuntimeError(f'gfx render failed {out}')
    return out

if __name__ == '__main__':
    import sys
    tests = {'title': title_card(), 'big': big_number(61, 'Goals', 'Harry Kane · all competitions 2025/26'),
             'vs': versus('Kane', 'Yamal', [('Goals', '61', '24', 'l'), ('World Cup', 'Semi-final', 'Winner', 'r')]),
             'exhibit': exhibit('A', 'La Liga'), 'gravity': gravity(), 'trophy': trophy_cabinet(), 'criteria': criteria(),
             'odds': odds_board(), 'window': window_timeline(), 'stack': stat_stack([('16', 'goals'), ('11', 'assists')], 'La Liga 2025/26')}
    outdir = P/'_tmp'/'gfx_test'; outdir.mkdir(parents=True, exist_ok=True)
    bg = Image.new('RGBA', (W, H), (60, 90, 70, 255))
    for k, g in tests.items():
        for tt in ([1.0, 3.5] if k != 'gravity' else [1, 3, 5.5]):
            fr = bg.copy(); fr.alpha_composite(g(tt, 6.0)); fr.convert('RGB').resize((960, 540)).save(outdir/f'{k}_{tt}.jpg')
    print('ok')
