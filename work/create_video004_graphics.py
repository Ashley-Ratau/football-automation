from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Video 004 - Pep Guardiola Warned Us About Lamine Yamal" / "assets" / "editor_package" / "graphics"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
RED = (202, 30, 42)
BLUE = (34, 86, 190)
DARK = (15, 17, 22)
WHITE = (246, 246, 246)
MUTE = (178, 182, 190)
GOLD = (238, 190, 65)
GREEN = (38, 162, 92)


def font(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf", size)


FT = font(86, True)
FB = font(64, True)
FM = font(44, True)
FS = font(34)
FXS = font(28)


def base(title, subtitle):
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=DARK)
    draw.rectangle([0, 0, 18, H], fill=RED)
    draw.rectangle([18, 0, 28, H], fill=BLUE)
    draw.text((95, 80), title, font=FT, fill=WHITE)
    draw.text((100, 184), subtitle, font=FS, fill=MUTE)
    return img, draw


def centered(draw, xy, text, fnt, fill):
    x, y = xy
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (box[2] - box[0]) / 2, y), text, font=fnt, fill=fill)


def timeline():
    img, draw = base("THE LAMINE TIMELINE", "The hype moved faster than a normal career")
    xs = [270, 690, 1110, 1530]
    labels = [("16", "Breaks through"), ("17", "Barcelona depends"), ("18", "Spain expects"), ("NOW", "World Cup pressure")]
    y = 565
    draw.line([(xs[0], y), (xs[-1], y)], fill=(90, 94, 104), width=8)
    for x, (age, text) in zip(xs, labels):
        draw.ellipse([x - 38, y - 38, x + 38, y + 38], fill=GOLD if age == "NOW" else RED)
        centered(draw, (x, y - 150), age, FB, WHITE)
        centered(draw, (x, y + 82), text, FS, MUTE)
    draw.text((100, 930), "Use after the first Pep warning insert.", font=FXS, fill=(122, 126, 134))
    img.save(OUT / "graphic_lamine_timeline.png", quality=95)


def pressure_map():
    img, draw = base("THE PRESSURE MAP", "Why the Messi comparison is not just praise")
    items = [
        ("BARCELONA", "Need a new identity"),
        ("SPAIN", "Need a World Cup spark"),
        ("MEDIA", "Need the next Messi"),
        ("FANS", "Need magic every game"),
        ("DEFENDERS", "Now study every move"),
        ("BODY", "Still developing"),
    ]
    x0, y0, cw, ch = 125, 330, 500, 155
    for i, (head, body) in enumerate(items):
        x = x0 + (i % 3) * (cw + 70)
        y = y0 + (i // 3) * (ch + 80)
        draw.rectangle([x, y, x + cw, y + ch], fill=(32, 35, 42), outline=(76, 82, 96), width=2)
        draw.text((x + 28, y + 26), head, font=FM, fill=WHITE)
        draw.text((x + 28, y + 92), body, font=FS, fill=MUTE)
    draw.rectangle([610, 850, 1310, 940], fill=RED)
    draw.text((660, 872), "PRESSURE WEARING A CROWN", font=FM, fill=WHITE)
    img.save(OUT / "graphic_pressure_map.png", quality=95)


def use_vs_depend():
    img, draw = base("USE HIM OR DEPEND ON HIM?", "Spain's real World Cup test")
    draw.rectangle([120, 315, 900, 835], fill=(31, 35, 42), outline=GREEN, width=4)
    draw.rectangle([1020, 315, 1800, 835], fill=(31, 35, 42), outline=RED, width=4)
    draw.text((180, 375), "USE LAMINE", font=FB, fill=WHITE)
    draw.text((1080, 375), "DEPEND ON LAMINE", font=FB, fill=WHITE)
    left = ["Give him conditions", "Stretch both sides", "Let Pedri and Rodri control", "Protect his freedom"]
    right = ["Every attack finds him", "Every mistake becomes news", "Messi comparisons grow", "The joy becomes a job"]
    for n, item in enumerate(left):
        y = 505 + n * 68
        draw.ellipse([180, y + 12, 200, y + 32], fill=GREEN)
        draw.text((225, y), item, font=FS, fill=MUTE)
    for n, item in enumerate(right):
        y = 505 + n * 68
        draw.ellipse([1080, y + 12, 1100, y + 32], fill=RED)
        draw.text((1125, y), item, font=FS, fill=MUTE)
    draw.text((100, 944), "Use near the final third when the solution is explained.", font=FXS, fill=(122, 126, 134))
    img.save(OUT / "graphic_use_vs_depend.png", quality=95)


if __name__ == "__main__":
    timeline()
    pressure_map()
    use_vs_depend()
    print("created graphics")
