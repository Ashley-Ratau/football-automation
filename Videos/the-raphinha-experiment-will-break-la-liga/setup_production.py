"""Configure the new production without reading the rejected project."""
from pathlib import Path
import json, shutil

P = Path(__file__).resolve().parent
REFERENCE = P.parent / 'barcelona-are-more-dangerous-than-you-think'
for name in ['music_original.mp3', 'music_normalized.wav', 'music_provenance.json']:
    shutil.copy2(REFERENCE/'assets'/name, P/'assets'/name)
cfg = json.loads((P/'long_form_project.json').read_text(encoding='utf-8-sig'))
cfg['music_bed'] = 'assets/music_original.mp3'
cfg['settings'].update(voice_speed=1.0, min_duration_seconds=480, max_duration_seconds=660,
                       broll_clip_max_seconds=3.8, insert_fade_seconds=0.12)
cfg['captions']['enabled'] = False
(P/'long_form_project.json').write_text(json.dumps(cfg, indent=2), encoding='utf-8')
print('Production settings and approved original music ready.')
