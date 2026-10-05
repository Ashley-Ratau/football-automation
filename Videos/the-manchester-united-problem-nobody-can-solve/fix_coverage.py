import json
from pathlib import Path
p=Path(__file__).parent/'long_form_project.json'; c=json.loads(p.read_text(encoding='utf-8-sig'))
for s in c['sections']:
    if s['name']=='conclusion':
        x=dict(s['broll'][-1]); x['duration']=2.0; s['broll'].append(x)
p.write_text(json.dumps(c,indent=2),encoding='utf-8')
