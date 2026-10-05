from __future__ import annotations
import subprocess, re, sys
from pathlib import Path
from PIL import Image
import numpy as np

FF = r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BASE = Path(r"C:\Users\Wendy\Documents\Football Channel\pep_guardiola_ferran_torres_short")
Q = BASE / "final video" / "qc" / "source"


def dur(p):
    r = subprocess.run([FF, "-i", str(p)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0


def analyze(img_path):
    img = np.asarray(Image.open(img_path).convert("RGB")).astype(float)
    mean = img.mean()
    std = img.std()
    r, g, b = img[..., 0].mean(), img[..., 1].mean(), img[..., 2].mean()
    dark = (img.mean(axis=2) < 25).mean() * 100
    return dict(mean=round(mean, 1), std=round(std, 1),
                r=round(r, 1), g=round(g, 1), b=round(b, 1), dark_pct=round(dark, 1))


def sample(src, step=5, max_t=480):
    print(f"\n### {src.name}  ({dur(src):.1f}s)")
    Q.mkdir(parents=True, exist_ok=True)
    t = 0
    rows = []
    while t < max_t and t < dur(src):
        f = Q / f"{src.stem}_{t:04d}.jpg"
        subprocess.run([FF, "-y", "-ss", str(t), "-i", str(src),
                        "-frames:v", "1", "-update", "1", str(f)],
                       capture_output=True)
        a = analyze(f)
        flags = []
        if a["mean"] < 30:
            flags.append("BLACK")
        if a["std"] < 18:
            flags.append("FLAT")
        rows.append((t, a, flags))
        t += step
    for t, a, flags in rows:
        flag_s = ",".join(flags) if flags else "-"
        print(f"{t:>6}  {a['mean']:>6} {a['std']:>6} {a['r']:>5} {a['g']:>5} {a['b']:>5} {a['dark_pct']:>6}  {flag_s}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "interview"
    src = BASE / "assets" / "raw" / f"{which}.mp4"
    sample(src)
