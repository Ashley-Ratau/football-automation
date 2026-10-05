"""Minimal documentary graphics: quote cards, kinetic text, date tags, title and end card (RGBA, 1920x1080)."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = Path(__file__).resolve().parent
FF = r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
W, H, FPS = 1920, 1080, 30
F = P/'assets'/'fonts'
WHITE = (242, 240, 235); GREY = (165, 165, 170); RED = (219, 0, 7); GOLD = (232, 189, 82)
_fc = {}
def font(name, size, var=None):
    k = (name, size, tuple(var) if var else None)
    if k not in _fc:
        f = ImageFont.truetype(str(F/name), size)
        if var:
            try: f.set_variation_by_axes(var)
            except Exception: pass
        _fc[k] = f
    return _fc[k]
ANTON = lambda s: font('Anton-Regular.ttf', s)
INTER = lambda s, w=500: font('Inter.ttf', s, [28, w])

def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, a, l): return clamp((t - a) / l)

def text_img(txt, fnt, fill, shadow=12, italic=False):
    b = fnt.getbbox(txt); w, h = b[2] - b[0] + 60, b[3] - b[1] + 60
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((30 - b[0], 30 - b[1]), txt, font=fnt, fill=(0, 0, 0, 200))
    if shadow: im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)), (0, 4))
    ImageDraw.Draw(im).text((30 - b[0], 30 - b[1]), txt, font=fnt, fill=fill + (255,))
    if italic: im = im.transform(im.size, Image.AFFINE, (1, 0.18, -0.09 * h, 0, 1, 0), Image.BICUBIC)
    return im

def put(base, layer, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0: return
    if scale != 1: layer = layer.resize((int(layer.width * scale), int(layer.height * scale)), Image.LANCZOS)
    if alpha < 1:
        layer = layer.copy(); layer.putalpha(layer.getchannel('A').point(lambda v: int(v * alpha)))
    base.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))

def kinetic(text, color=WHITE, size=120, sub=None):
    """Short italic phrase that fades/slides in (Mourinho-reference style)."""
    def draw(t, dur):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        a = ease(prog(t, 0.05, 0.45)) * (1 - prog(t, dur - 0.35, 0.35))
        put(im, text_img(text, ANTON(size), color, italic=True), W / 2 + 40 * (1 - ease(prog(t, 0, 0.5))), H / 2, a)
        if sub: put(im, text_img(sub, INTER(40, 500), GREY), W / 2, H / 2 + size * 0.85, a)
        return im
    return draw

def date_tag(text):
    """Small top-left tag naming the speaker and date of a soundbite."""
    def draw(t, dur):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        a = ease(prog(t, 0.2, 0.4)) * (1 - prog(t, 3.6, 0.5))
        if a <= 0: return im
        d = ImageDraw.Draw(im); lay = text_img(text.upper(), INTER(34, 700), WHITE, shadow=0)
        box = Image.new('RGBA', (lay.width + 10, 70), (12, 12, 14, int(205 * a)))
        im.alpha_composite(box, (70, 70)); d.rectangle([70, 70, 77, 140], fill=RED + (int(255 * a),))
        put(im, lay, 70 + 8 + lay.width / 2, 105, a)
        return im
    return draw

def wrap(lines): return lines

def quote_card(lines, credit):
    """Paper-style quote card that types in line by line."""
    def draw(t, dur):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        a = ease(prog(t, 0, 0.4))
        card = Image.new('RGBA', (1400, 120 + 115 * len(lines) + 90), (238, 234, 225, int(250 * a)))
        cd = ImageDraw.Draw(card)
        step = max(0.6, (dur - 2.0) / len(lines))
        for i, ln in enumerate(lines):
            la = ease(prog(t, 0.4 + i * step, 0.5))
            if la <= 0: continue
            lay = text_img(ln, font('Inter.ttf', 54, [28, 600]), (20, 20, 22), shadow=0)
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * la)))
            card.alpha_composite(lay, (60, 60 + i * 115))
        ca = ease(prog(t, 0.6 + len(lines) * step * 0.6, 0.5))
        cl = text_img('— ' + credit, INTER(34, 500), (90, 90, 95), shadow=0); cl.putalpha(cl.getchannel('A').point(lambda v: int(v * ca)))
        card.alpha_composite(cl, (60, card.height - 100))
        cd.rectangle([0, 0, 10, card.height], fill=RED + (int(255 * a),))
        sh = Image.new('RGBA', (card.width + 80, card.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([40, 50, card.width + 40, card.height + 40], fill=(0, 0, 0, int(160 * a)))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25)), ((W - card.width) // 2 - 40, (H - card.height) // 2 - 40))
        s = 0.96 + 0.04 * ease(prog(t, 0, 0.6))
        put(im, card, W / 2, H / 2, 1, s)
        return im
    return draw

def title(text_a, text_b):
    def draw(t, dur):
        im = Image.new('RGBA', (W, H), (0, 0, 0, int(120 * ease(prog(t, 0, 0.3)))))
        put(im, text_img(text_a, ANTON(190), WHITE), W / 2, H / 2 - 90, ease(prog(t, 0.1, 0.35)), 1.15 - 0.15 * ease(prog(t, 0.1, 0.35)))
        put(im, text_img(text_b, ANTON(190), RED), W / 2, H / 2 + 110, ease(prog(t, 0.55, 0.35)), 1.15 - 0.15 * ease(prog(t, 0.55, 0.35)))
        return im
    return draw

def render(draw, dur, out):
    n = max(1, round(dur * FPS))
    p = subprocess.Popen([FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-frames:v', str(n), '-c:v', 'qtrle', str(out)], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(n): p.stdin.write(draw(i / FPS, dur).tobytes())
    p.stdin.close(); p.wait()
    return out

if __name__ == '__main__':
    bg = Image.new('RGBA', (W, H), (70, 70, 75, 255)); out = P/'_tmp'/'gfx_test'; out.mkdir(parents=True, exist_ok=True)
    tests = {'kin': kinetic('£900 MILLION', sub='inflated revenues, reduced costs'), 'tag': date_tag('Arsène Wenger · July 2011'),
             'card': quote_card(['\u201cIf financial fair play is to have a chance,', 'the sponsorship has to be at the market price.', 'It cannot be doubled, tripled or quadrupled.\u201d'], 'Arsène Wenger · July 2011 · via The Guardian'),
             'title': title('WENGER', 'KNEW')}
    for k, g in tests.items():
        fr = bg.copy(); fr.alpha_composite(g(2.5, 7.0)); fr.convert('RGB').resize((960, 540)).save(out/f'{k}.jpg')
    print('ok')
