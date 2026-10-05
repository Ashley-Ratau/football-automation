from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Video 003 - Gary Neville Warned Us About Ronaldo" / "assets" / "editor_package" / "graphics"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
RED = (198, 24, 35)
DARK = (16, 18, 22)
WHITE = (245, 245, 245)
MUTE = (175, 178, 185)
GOLD = (238, 190, 65)
GREEN = (35, 160, 88)


def font(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf", size)


FT = font(92, True)
FB = font(68, True)
FM = font(46, True)
FS = font(34)
FXS = font(28)


def base(title, subtitle):
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=DARK)
    draw.rectangle([0, 0, 18, H], fill=RED)
    draw.rectangle([18, 0, 26, H], fill=GOLD)
    draw.text((95, 80), title, font=FT, fill=WHITE)
    draw.text((100, 190), subtitle, font=FS, fill=MUTE)
    return img, draw


def centered(draw, xy, text, fnt, fill):
    x, y = xy
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (box[2] - box[0]) / 2, y), text, font=fnt, fill=fill)


def warning_timeline():
    img, draw = base("THE WARNING TIMELINE", "Why this debate did not start with one missed chance")
    xs = [280, 760, 1240, 1660]
    labels = [
        ("2022", "Benched at the World Cup"),
        ("2024", "The debate never left"),
        ("2026", "Portugal still orbit him"),
        ("NOW", "Respect vs reality"),
    ]
    y = 560
    draw.line([(xs[0], y), (xs[-1], y)], fill=(90, 94, 104), width=8)
    for x, (year, text) in zip(xs, labels):
        draw.ellipse([x - 36, y - 36, x + 36, y + 36], fill=RED if year != "NOW" else GOLD)
        centered(draw, (x, y - 150), year, FB, WHITE)
        centered(draw, (x, y + 82), text, FS, MUTE)
    draw.text((100, 930), "Use after the Neville warning is introduced.", font=FXS, fill=(120, 124, 132))
    img.save(OUT / "graphic_warning_timeline.png", quality=95)


def talent_map():
    img, draw = base("PORTUGAL HAVE THE TALENT", "The question is whether the system is free enough to use it")
    players = [
        ("BRUNO", "Chance creation"),
        ("BERNARDO", "Control"),
        ("VITINHA", "Tempo"),
        ("LEAO", "Chaos"),
        ("NUNO", "Width"),
        ("RAMOS", "Penalty box"),
        ("JOAO NEVES", "Energy"),
    ]
    x0, y0 = 110, 330
    card_w, card_h = 380, 155
    for i, (name, role) in enumerate(players):
        x = x0 + (i % 4) * (card_w + 55)
        y = y0 + (i // 4) * (card_h + 70)
        draw.rectangle([x, y, x + card_w, y + card_h], fill=(32, 35, 42), outline=(72, 76, 86), width=2)
        draw.text((x + 28, y + 28), name, font=FM, fill=WHITE)
        draw.text((x + 28, y + 92), role, font=FS, fill=MUTE)
    draw.rectangle([650, 840, 1270, 935], fill=RED)
    draw.text((708, 862), "NOT A ONE-MAN SQUAD", font=FM, fill=WHITE)
    img.save(OUT / "graphic_portugal_talent_map.png", quality=95)


def weapon_system():
    img, draw = base("WEAPON OR SYSTEM?", "The difference between using Ronaldo and becoming trapped by him")
    draw.rectangle([120, 310, 900, 830], fill=(31, 35, 42), outline=GREEN, width=4)
    draw.rectangle([1020, 310, 1800, 830], fill=(31, 35, 42), outline=RED, width=4)
    draw.text((180, 370), "RONALDO AS A WEAPON", font=FB, fill=WHITE)
    draw.text((1080, 370), "RONALDO AS THE SYSTEM", font=FB, fill=WHITE)
    for n, item in enumerate(["Used in moments", "Built around the game state", "Service when it makes sense", "Portugal keep variety"]):
        y = 500 + n * 68
        draw.ellipse([180, y + 12, 200, y + 32], fill=GREEN)
        draw.text((225, y), item, font=FS, fill=MUTE)
    for n, item in enumerate(["Every attack bends to him", "Crosses become default", "Teammates hesitate", "The team loses rhythm"]):
        y = 500 + n * 68
        draw.ellipse([1080, y + 12, 1100, y + 32], fill=RED)
        draw.text((1125, y), item, font=FS, fill=MUTE)
    draw.text((100, 940), "Use near the final third when the script shifts from blame to the solution.", font=FXS, fill=(120, 124, 132))
    img.save(OUT / "graphic_weapon_vs_system.png", quality=95)


if __name__ == "__main__":
    for old in OUT.glob("test.png"):
        old.unlink()
    warning_timeline()
    talent_map()
    weapon_system()
    print("created graphics")
