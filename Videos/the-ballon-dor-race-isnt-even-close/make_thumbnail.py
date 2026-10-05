"""1280x720 thumbnails: Yamal with the World Cup in front, Kane faded behind, one oversized word."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from rembg import remove

P = Path(__file__).resolve().parent
T = P/'assets'/'thumbnail'; FR = T/'frames'
W, H = 1280, 720
GOLD = (240, 196, 80)

def cut(path, box):
    im = Image.open(path).convert('RGB').crop(box)
    cache = T/(Path(path).stem + f'_{box[0]}_cut.png')
    if cache.exists(): return Image.open(cache)
    out = remove(im); out.save(cache); return out

def glow(layer, color, radius):
    a = layer.getchannel('A').filter(ImageFilter.GaussianBlur(radius))
    g = Image.new('RGBA', layer.size, color + (0,)); g.putalpha(a); return g

def make(word, name, word_color=GOLD, sub=None):
    bg = Image.new('RGBA', (W, H), (12, 12, 16, 255))
    # backdrop: blurred stadium from trophy celebration
    st = Image.open(FR/'y_383.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(18))
    st = ImageEnhance.Brightness(st).enhance(0.35); bg.paste(st)
    # radial gold light behind yamal
    light = Image.new('L', (W, H), 0); ImageDraw.Draw(light).ellipse([560, 40, 1300, 780], fill=150)
    light = light.filter(ImageFilter.GaussianBlur(120))
    bg.alpha_composite(Image.merge('RGBA', (*Image.new('RGB', (W, H), (200, 150, 50)).split(), light)))
    # giant word behind heads
    d = ImageDraw.Draw(bg)
    f = ImageFont.truetype(str(P/'assets'/'fonts'/'Anton-Regular.ttf'), 300)
    bb = d.textbbox((0, 0), word, font=f); tw = bb[2] - bb[0]
    d.text(((W - tw) / 2 - bb[0], 10 - bb[1] + 20), word, font=f, fill=word_color + (255,))
    # Kane: desaturated, darker, left, behind
    k = Image.open(T/'kane_cut.png'); k.putalpha(k.getchannel('A').point(lambda v: 255 if v > 140 else 0).filter(ImageFilter.GaussianBlur(1.5)))
    k = k.resize((int(k.width * 0.6), int(k.height * 0.6)), Image.LANCZOS)
    rgb = ImageEnhance.Brightness(ImageOps.grayscale(k.convert('RGB')).convert('RGB')).enhance(0.6)
    rgb = Image.blend(rgb, Image.new('RGB', rgb.size, (90, 20, 30)), 0.18); rgb.putalpha(k.getchannel('A'))
    bg.alpha_composite(rgb, (-130, H - rgb.height + 30))
    # Yamal with trophy: big, right, bright
    y = Image.open(T/'yamal_cut.png'); y.putalpha(y.getchannel('A').point(lambda v: 255 if v > 140 else 0).filter(ImageFilter.GaussianBlur(1.5)))
    sc = 640 / y.height; y = y.resize((int(y.width * sc), 640), Image.LANCZOS)
    y = Image.merge('RGBA', (*ImageEnhance.Contrast(ImageEnhance.Color(y.convert('RGB')).enhance(1.2)).enhance(1.1).split(), y.getchannel('A')))
    gx, gy = 330, H - y.height + 10
    bg.alpha_composite(y, (gx, gy))
    if sub:
        fs = ImageFont.truetype(str(P/'assets'/'fonts'/'Anton-Regular.ttf'), 70)
        tb = d.textbbox((0, 0), sub, font=fs)
        x0, y0 = 40, H - 140
        d = ImageDraw.Draw(bg); d.rectangle([x0 - 10, y0 - 8, x0 + tb[2] - tb[0] + 20, y0 + tb[3] - tb[1] + 22], fill=(220, 30, 50, 255))
        d.text((x0 + 5 - tb[0], y0 - tb[1] + 6), sub, font=fs, fill=(255, 255, 255, 255))
    # vignette
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).rectangle([0, 0, W, H], fill=255)
    v = ImageOps.invert(Image.new('L', (W, H), 0).point(lambda _: 0))
    out = bg.convert('RGB'); out.save(T/f'{name}.jpg', quality=93); return out

if __name__ == '__main__':
    make('CLOSE?', 'thumb_A_close')
    make('NOT CLOSE', 'thumb_B_not_close')
    make('CLOSE?', 'thumb_C_close_kane_wrong', sub='THE ODDS ARE WRONG')
    print('ok')
