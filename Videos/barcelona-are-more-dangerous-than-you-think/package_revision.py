import json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
thumbs=P/'assets/thumbnail/v2'
ids=[int(p.stem.split('_')[-1]) for p in sorted(thumbs.glob('thumbnail_0*.png'))]
assert ids
html=(P/'START_HERE.html').read_text(encoding='utf-8-sig')
html=html.replace('for(let i=2;i<=5;i++)',f'for(const i of {json.dumps(ids)})')
html=html.replace('assets/thumbnail/thumbnail_${num}.png','assets/thumbnail/v2/thumbnail_${num}.png')
html=html.replace('Football Channel / Local review','Football Channel / Revised edition')
html=html.replace('Each thumbnail appears automatically when its local image file is available.','Revised directions: realistic players, expressive match moments, minimal backgrounds and one-word headlines.')
html=html.replace('<h2>Thumbnail collection</h2>','<h2>Revised thumbnails</h2>')
html=html.replace('<footer class="footer">','<p class="note"><a class="download" href="versions/v1/barcelona-are-more-dangerous-than-you-think.mp4">Compare with the original video</a></p><footer class="footer">')
(P/'START_HERE.html').write_text(html,encoding='utf-8')
shutil.copy2(thumbs/'thumbnail_01.png',P/'assets/thumbnail/thumbnail_primary.png')
print('Revision packaged')
