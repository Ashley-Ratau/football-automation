import json, shutil, subprocess
from pathlib import Path

P=Path(__file__).parent
cfgp=P/'long_form_project.json'
cfg=json.loads(cfgp.read_text(encoding='utf-8-sig'))
old=cfg['sections']
by={s['name']:s for s in old}

# Replace every tactical graphic with real match footage, using the existing match clips as coverage.
pool=[]
for s in old:
    for item in s.get('broll',[]):
        if not Path(item['file']).stem.startswith('tactics_') and item['file'] not in [x['file'] for x in pool]:
            pool.append(item)
for s in old:
    if s['type']!='vo': continue
    cleaned=[]
    for item in s.get('broll',[]):
        if Path(item['file']).stem.startswith('tactics_'):
            repl=dict(pool[len(cleaned)%len(pool)])
            repl['duration']=item.get('duration',4.2)
            cleaned.append(repl)
        else: cleaned.append(item)
    s['broll']=cleaned

# Split the cold open narration so the first insert lands at ~30 seconds.
src=P/'assets'/'vo'/'01_cold_open_raw.wav'
head=P/'assets'/'vo'/'01_cold_open_head_raw.wav'; tail=P/'assets'/'vo'/'03_cold_open_tail_raw.wav'
subprocess.run(['ffmpeg','-y','-i',str(src),'-t','30',str(head)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run(['ffmpeg','-y','-i',str(src),'-ss','30',str(tail)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
head_s=dict(by['cold_open']); head_s['name']='cold_open_head'; head_s['text']=head_s['text'][:430]; head_s['broll']=head_s['broll']
tail_s=dict(by['cold_open']); tail_s['name']='cold_open_tail'; tail_s['text']=tail_s['text'][430:]; tail_s['broll']=tail_s['broll']
insert=dict(by['neville_experiments'])
sections=[head_s,insert,tail_s]+[s for s in old if s['name'] not in ('cold_open','neville_experiments')]
cfg['sections']=sections
cfg['captions']['enabled']=True
cfg['captions']['group_size']=4
cfg['output_filename']='why-every-manchester-united-rebuild-fails-match-broll-captions.mp4'
cfgp.write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding='utf-8')

# Copy cached processed VO under the new section numbering/names expected by the builder.
for i,s in enumerate(sections,1):
    if s['type']!='vo': continue
    dest=P/'assets'/'vo'/f'{i:02d}_{s["name"]}_raw.wav'
    if s['name']=='cold_open_head': shutil.copy2(head,dest)
    elif s['name']=='cold_open_tail': shutil.copy2(tail,dest)
    else:
        orig=by[s['name']]['name'] if s['name'] in by else s['name']
        candidates=list((P/'assets'/'vo').glob(f'*_{orig}_raw.wav'))
        if candidates: shutil.copy2(candidates[0],dest)
print('updated config:',len(sections),'sections; captions enabled; tactical graphics replaced')
