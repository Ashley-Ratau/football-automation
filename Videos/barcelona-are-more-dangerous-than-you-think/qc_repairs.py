import json,subprocess
from PIL import Image,ImageDraw
from pathlib import Path
P=Path(__file__).resolve().parent
shots=json.loads((P/'shot_timeline.json').read_text())
report=json.loads((P/'final video/build_report.json').read_text())
offsets={};elapsed=0
for s in report['timeline']:
    offsets[s['name']]=elapsed;elapsed+=s['duration']
raw_offsets={}
for s in shots:raw_offsets.setdefault(s['section'],s['timeline_start'])
selected=[s for s in shots if (s['section'],s['narration_anchor']) in [('hook','Seven competitive'),('raphinha_space','Against Racing'),('raphinha_space','Against Feyenoord'),('midfield_choices','The pass'),('additional_weapons','He settled'),('additional_weapons','Gabriel Jesus'),('payoff','The numbers')]]
sheet=Image.new('RGB',(1280,240*((len(selected)+3)//4)),'#101722');draw=ImageDraw.Draw(sheet)
for i,s in enumerate(selected):
    t=offsets[s['section']]+s['timeline_start']-raw_offsets[s['section']]+s['duration']/2
    path=P/'_tmp/qc_full'/f'repair_{i:02d}.jpg'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(P/'final video/barcelona-are-more-dangerous-than-you-think.mp4'),'-frames:v','1','-vf','scale=320:180',str(path)],check=True)
    x=i%4*320;y=i//4*240
    with Image.open(path) as im:sheet.paste(im,(x,y))
    draw.text((x+4,y+184),f'{t:.1f}s {s["section"]}\n{s["narration_anchor"]}',fill='white')
sheet.save(P/'_tmp/qc_full/repairs_contact.jpg')
print('Checked',len(selected),'repaired shots')
