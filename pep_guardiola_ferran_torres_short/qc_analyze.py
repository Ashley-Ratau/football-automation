from __future__ import annotations
import subprocess, sys
from pathlib import Path
from PIL import Image
import numpy as np

FF = r"C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BASE = Path(r"C:\Users\Wendy\Documents\Football Channel\pep_guardiola_ferran_torres_short")
OUT = BASE / "final video" / "pep_guardiola_ferran_torres_9x16.mp4"
Q = BASE / "final video" / "qc"


def dur(p):
    r = subprocess.run([FF, "-i", str(p)], capture_output=True, text=True)
    import re
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


def main():
    Q.mkdir(exist_ok=True)
    total = dur(OUT)
    print(f"OUT: {OUT}  ({total:.1f}s)")
    step = 5
    rows = []
    t = 0
    while t < total:
        f = Q / f"f_{t:04d}s.jpg"
        subprocess.run([FF, "-y", "-ss", str(t), "-i", str(OUT),
                        "-frames:v", "1", "-update", "1", str(f)],
                       capture_output=True)
        a = analyze(f)
        flags = []
        if a["mean"] < 30:
            flags.append("BLACK")
        if a["std"] < 18:
            flags.append("LOW-CONTRAST/FLAT")
        if abs(a["r"] - a["g"]) < 4 and abs(a["g"] - a["b"]) < 4 and a["std"] < 30:
            flags.append("GREYISH")
        rows.append((t, a, flags))
        t += step
    print(f"\n{'t':>6}  {'mean':>6} {'std':>6} {'R':>5} {'G':>5} {'B':>5} {'dark%':>6}  flags")
    for t, a, flags in rows:
        flag_s = ",".join(flags) if flags else "-"
        print(f"{t:>6}  {a['mean']:>6} {a['std']:>6} {a['r']:>5} {a['g']:>5} {a['b']:>5} {a['dark_pct']:>6}  {flag_s}")


if __name__ == "__main__":
    main()
