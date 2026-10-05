"""Mirror live-action B-roll, blur corner broadcast marks, and add light vignette."""
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
edit = Path(__file__).resolve().parent
source = root / 'final video' / 'the-raphinha-experiment-will-break-la-liga.mp4'
shots = json.loads((root / 'shot_timeline.json').read_text(encoding='utf-8-sig'))
sections = json.loads((root / 'final video' / 'build_report.json').read_text(encoding='utf-8-sig'))['timeline']

groups = {'mirror': [], 'broadcast': [], 'training': []}
offset = 0.0
for section in sections:
    section_shots = [s for s in shots if s['section'] == section['name']]
    if section['type'] == 'vo':
        scale = float(section['duration']) / sum(float(s['duration']) for s in section_shots)
        local = 0.0
        for shot in section_shots:
            duration = float(shot['duration']) * scale
            start, end = offset + local, offset + local + duration
            name = Path(shot['file']).name
            if not name.startswith('tactics_'):
                groups['mirror'].append((start, end))
            if name in ('sevilla_current_1_3.mp4', 'raphinha_best_2025_26.mp4'):
                groups['broadcast'].append((start, end))
            elif name in ('raphinha_group_training.mp4', 'raphinha_training_spotlight.mp4'):
                groups['training'].append((start, end))
            local += duration
    offset += float(section['duration'])

def expression(windows):
    merged = []
    for start, end in windows:
        if merged and start - merged[-1][1] < 0.035:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    terms = []
    for start, end in merged:
        a = round((start + .015) * 30) / 30
        b = round((end - .015) * 30) / 30
        if b > a:
            terms.append(f'between(t,{a:.3f},{b:.3f})')
    return '+'.join(terms)

mirror = expression(groups['mirror'])
broadcast = expression(groups['broadcast'])
training = expression(groups['training'])

def mask(name, width, height, fade_left=0, fade_right=0, fade_top=0, fade_bottom=0):
    picture = Image.new('L', (width, height))
    px = picture.load()
    for y in range(height):
        for x in range(width):
            a = 1.0
            if fade_left:
                a = min(a, x / fade_left)
            if fade_right:
                a = min(a, (width - 1 - x) / fade_right)
            if fade_top:
                a = min(a, y / fade_top)
            if fade_bottom:
                a = min(a, (height - 1 - y) / fade_bottom)
            px[x, y] = max(0, min(255, round(255 * a)))
    path = edit / name
    picture.save(path)
    return path

mask_paths = [
    mask('mask_broadcast_left.png', 650, 250, fade_right=55, fade_bottom=45),
    mask('mask_training_left.png', 320, 180, fade_right=45, fade_bottom=40),
    mask('mask_broadcast_right.png', 690, 260, fade_left=55, fade_bottom=50),
    mask('mask_broadcast_lower_left.png', 400, 150, fade_right=55, fade_top=40),
]
f = (
    '[0:v]split=2[base][flipin];'
    '[flipin]hflip[flipped];'
    f"[base][flipped]overlay=0:0:enable='{mirror}':shortest=1,"
    'vignette=angle=PI/5,split=5[main][btl][tltl][btr][bbl];'
    '[btl]crop=650:250:0:0,boxblur=luma_radius=16:luma_power=2:chroma_radius=10:chroma_power=1[btlsoft];'
    '[tltl]crop=320:180:0:0,boxblur=luma_radius=16:luma_power=2:chroma_radius=10:chroma_power=1[tltlsoft];'
    '[btr]crop=690:260:1230:0,boxblur=luma_radius=16:luma_power=2:chroma_radius=10:chroma_power=1[btrsoft];'
    '[bbl]crop=400:150:0:930,boxblur=luma_radius=14:luma_power=2:chroma_radius=9:chroma_power=1[bblsoft];'
    '[1:v]format=gray[m1];[2:v]format=gray[m2];[3:v]format=gray[m3];[4:v]format=gray[m4];'
    '[btlsoft][m1]alphamerge[btlb];'
    '[tltlsoft][m2]alphamerge[tltlb];'
    '[btrsoft][m3]alphamerge[btrb];'
    '[bblsoft][m4]alphamerge[bblb];'
    f"[main][btlb]overlay=0:0:enable='{broadcast}':shortest=1[o1];"
    f"[o1][tltlb]overlay=0:0:enable='{training}':shortest=1[o2];"
    f"[o2][btrb]overlay=1230:0:enable='{broadcast}':shortest=1[o3];"
    f"[o3][bblb]overlay=0:930:enable='{broadcast}':shortest=1,format=yuv420p,subtitles=captions.ass[outv]"
)
filter_path = edit / 'blur_mirror_filter.txt'
filter_path.write_text(f, encoding='utf-8')

parser = argparse.ArgumentParser()
parser.add_argument('--preview-seconds', type=float)
args = parser.parse_args()
output = edit / ('soft_blur_caption_preview.mp4' if args.preview_seconds else 'the-raphinha-experiment-soft-blur-captions.mp4')
cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(source)]
for path in mask_paths:
    cmd.extend(['-loop', '1', '-framerate', '30', '-i', str(path)])
cmd.extend(['-filter_complex_script', str(filter_path), '-map', '[outv]', '-map', '0:a:0',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-c:a', 'copy',
       '-movflags', '+faststart'])
if args.preview_seconds:
    cmd.extend(['-t', str(args.preview_seconds)])
cmd.append(str(output))
print(output, flush=True)
subprocess.run(cmd, check=True, cwd=edit)
