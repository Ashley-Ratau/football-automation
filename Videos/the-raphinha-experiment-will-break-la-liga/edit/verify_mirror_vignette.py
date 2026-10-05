from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
original = cv2.VideoCapture(str(root / 'final video' / 'the-raphinha-experiment-will-break-la-liga.mp4'))
test_name = sys.argv[1] if len(sys.argv) > 1 else 'the-raphinha-experiment-mirror-vignette.mp4'
test = cv2.VideoCapture(str(root / 'edit' / test_name))
times = [5, 16, 18, 23, 40, 100, 182, 210, 275, 400, 470]
canvas = Image.new('RGB', (960, 270 * len(times)))
draw = ImageDraw.Draw(canvas)
for i, second in enumerate(times):
    frames = []
    for cap in (original, test):
        cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f'Missing frame at {second}s')
        frames.append(cv2.cvtColor(cv2.resize(frame, (480, 270)), cv2.COLOR_BGR2RGB))
    canvas.paste(Image.fromarray(frames[0]), (0, i * 270))
    canvas.paste(Image.fromarray(frames[1]), (480, i * 270))
    draw.text((3, i * 270 + 3), f'{second}s ORIGINAL', fill='yellow')
    draw.text((483, i * 270 + 3), f'{second}s TEST', fill='yellow')
    old, new = (np.float32(x) for x in frames)
    direct = np.mean(np.abs(old - new))
    flipped = np.mean(np.abs(old[:, ::-1] - new))
    print(f'{second}s direct_MAE={direct:.1f} flipped_MAE={flipped:.1f} mirrored={flipped < direct}')
out = root / 'edit' / ('verify_blurred_contact.jpg' if 'blurred' in test_name else 'verify_contact.jpg')
canvas.save(out, quality=88)
print(out)
