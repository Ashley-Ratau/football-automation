"""Make a non-destructive mirrored B-roll / subtle-vignette test export."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDIT = Path(__file__).resolve().parent
SOURCE = ROOT / 'final video' / 'the-raphinha-experiment-will-break-la-liga.mp4'
OUTPUT = EDIT / 'the-raphinha-experiment-mirror-vignette.mp4'

shots = json.loads((ROOT / 'shot_timeline.json').read_text(encoding='utf-8-sig'))
report = json.loads((ROOT / 'final video' / 'build_report.json').read_text(encoding='utf-8-sig'))
sections = report['timeline']

# Reconcile editorial shot times with the frame-accurate rendered section lengths.
offset = 0.0
windows = []
for section in sections:
    section_shots = [s for s in shots if s['section'] == section['name']]
    if section['type'] == 'vo':
        coverage = sum(float(s['duration']) for s in section_shots)
        scale = float(section['duration']) / coverage
        local = 0.0
        for shot in section_shots:
            duration = float(shot['duration']) * scale
            # Tactical labels/arrows are deliberately kept readable.
            if '/tactics_' not in shot['file'].replace('\\', '/'):
                windows.append((offset + local, offset + local + duration))
            local += duration
    offset += float(section['duration'])

# Merge adjacent footage intervals; then stay one frame inside each boundary.
merged = []
for start, end in windows:
    if merged and start - merged[-1][1] < 0.035:
        merged[-1] = (merged[-1][0], end)
    else:
        merged.append((start, end))
terms = []
for start, end in merged:
    a = round((start + 0.015) * 30) / 30
    b = round((end - 0.015) * 30) / 30
    if b > a:
        terms.append(f'between(t,{a:.3f},{b:.3f})')
enable = '+'.join(terms)
filtergraph = (
    '[0:v]split=2[base][flipin];'
    '[flipin]hflip[flipped];'
    f"[base][flipped]overlay=x=0:y=0:enable='{enable}':shortest=1,"
    'vignette=angle=PI/5,format=yuv420p[outv]'
)
(EDIT / 'mirror_vignette_filter.txt').write_text(filtergraph, encoding='utf-8')
(EDIT / 'mirror_windows.json').write_text(json.dumps({'windows': merged, 'insert_sections': [s for s in sections if s['type'] == 'insert']}, indent=2), encoding='utf-8')

cmd = ['ffmpeg', '-y', '-i', str(SOURCE), '-filter_complex_script', str(EDIT / 'mirror_vignette_filter.txt'),
       '-map', '[outv]', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
       '-c:a', 'copy', '-movflags', '+faststart', str(OUTPUT)]
print(f'{len(merged)} mirrored B-roll windows; output: {OUTPUT}', flush=True)
subprocess.run(cmd, check=True)
