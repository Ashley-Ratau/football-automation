"""Select the approved polished Raphinha export and updated thumbnail for upload."""
import json
import shutil
from pathlib import Path

project = Path(__file__).resolve().parents[1]
selected = project / 'edit' / 'the-raphinha-experiment-soft-blur-captions.mp4'
published_copy = project / 'final video' / selected.name
thumbnail = project / 'assets' / 'thumbnail' / 'thumbnail_02.png'
config_path = project / 'long_form_project.json'

if not selected.exists() or not thumbnail.exists():
    raise FileNotFoundError('Selected video or updated thumbnail is missing')
shutil.copy2(selected, published_copy)

description = """Raphinha’s central role is giving Barcelona more ways to hurt a defence. His three goals against Sevilla showed three different movements—and three different decisions defenders have to make.

This film looks at Hansi Flick’s experiment, the supply from Lamine Yamal and Pedri, and what rivals must prepare for. Featuring perspectives from Shaka Hislop, Alejandro Moreno and Herculez Gomez.

Chapters
0:00 The experiment
0:33 Shaka Hislop — expert view
1:35 A winger through the middle
2:30 The defender’s decision
3:29 Alejandro Moreno — expert view
4:25 Three goals, three problems
5:29 What this means for La Liga
6:32 Herculez Gomez — expert view
7:30 Can anyone solve it?

Research cutoff: 20 September 2026. Tactical diagrams illustrate concepts; they are not tracking data. Footage and pundit excerpt credits are recorded in the project’s SOURCE_CREDITS.md.
"""

config = json.loads(config_path.read_text(encoding='utf-8-sig'))
config['output_filename'] = selected.name
config['thumbnail'] = 'assets/thumbnail/thumbnail_02.png'
config['upload']['title'] = 'The Raphinha Experiment Will Break La Liga'
config['upload']['description'] = description
config['upload']['privacy'] = 'private'
config['upload']['tags'] = ['Raphinha', 'FC Barcelona', 'Hansi Flick', 'La Liga', 'football analysis', 'Lamine Yamal']
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'video': str(published_copy), 'video_bytes': published_copy.stat().st_size,
                  'thumbnail': str(thumbnail), 'thumbnail_bytes': thumbnail.stat().st_size,
                  'title': config['upload']['title'], 'privacy': config['upload']['privacy']}, indent=2))
