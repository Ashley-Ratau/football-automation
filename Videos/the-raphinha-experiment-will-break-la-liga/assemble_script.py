from pathlib import Path
import json
P=Path(__file__).resolve().parent
draft=json.loads((P/'script_draft.json').read_text())
cfg=json.loads((P/'long_form_project.json').read_text(encoding='utf-8-sig'))
sections=[]
for s in draft:
    sections.append(dict(type='vo',**s,broll=[]))
    if s['name'] in ['hook','dilemma','league']:
        n=sum(x['type']=='insert' for x in sections)+1
        sections.append(dict(type='insert',name=f'pundit_{n}',file=f'assets/inserts/insert_{n}.mp4',start=0,end=55))
cfg['sections']=sections
(P/'long_form_project.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
(P/'03 script.md').write_text('# The Raphinha Experiment Will Break La Liga\n\nDraft narration; pundit sources and final transitions pending.\n\n'+'\n\n'.join('## '+s['chapter']+'\n\n'+s['text'] for s in draft),encoding='utf-8')
print('Six narration sections configured; three insert positions reserved.')
