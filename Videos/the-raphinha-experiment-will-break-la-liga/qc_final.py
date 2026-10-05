"""Measure the final artifact and create inspectable contact sheets for every cut."""
from pathlib import Path
import concurrent.futures,json,subprocess,wave
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;Q=P/'_tmp/final_qc';Q.mkdir(exist_ok=True)
cfg=json.loads((P/'long_form_project.json').read_text())
report=json.loads((P/'final video/build_report.json').read_text())
final=P/'final video'/cfg['output_filename']
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
segments=[];elapsed=0
for i,s in enumerate(cfg['sections'],1):
    path=P/'_tmp'/f'segment_{i:02d}_{s["name"]}.mp4';p=probe(path)
    duration=float(p['format']['duration']);segments.append(dict(name=s['name'],type=s['type'],start=elapsed,duration=duration))
    report['timeline'][i-1]['duration']=duration
    elapsed+=duration
(P/'final video/build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
timeline=[]
for s,seg in zip(cfg['sections'],segments):
    if s['type']=='insert':
        for n in [0.5,seg['duration']/2,seg['duration']-.5]:timeline.append(dict(time=seg['start']+n,label=s['name']+f' {n:.1f}s'))
    else:
        offset=0
        for item in s['broll']:
            timeline.append(dict(time=seg['start']+offset+item['duration']/2,label=item['label']))
            offset+=item['duration']
def grab(pair):
    i,item=pair;dest=Q/f'frame_{i:03d}.jpg'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(item['time']),'-i',str(final),'-frames:v','1','-vf','scale=320:180',str(dest)],check=True)
    return dest
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:frames=list(pool.map(grab,enumerate(timeline)))
for page in range((len(frames)+19)//20):
    sheet=Image.new('RGB',(1280,1050),(12,18,26));d=ImageDraw.Draw(sheet)
    for j,path in enumerate(frames[page*20:(page+1)*20]):
        i=page*20+j;x=(j%4)*320;y=(j//4)*210;sheet.paste(Image.open(path),(x,y))
        d.text((x+5,y+182),f'{timeline[i]["time"]:.2f}s {timeline[i]["label"]}',fill='white')
    sheet.save(Q/f'contact_{page+1:02d}.jpg',quality=92)
for name,args in [('audio',['-vn','-af','ebur128=peak=true']),('black',['-an','-vf','blackdetect=d=0.2:pix_th=0.10'])]:
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(final),*args,'-f','null','-'],capture_output=True,text=True)
    (Q/f'{name}.log').write_text(r.stderr,encoding='utf-8')
    if r.returncode:raise RuntimeError(name)
vo=0.0
for i,s in enumerate(cfg['sections'],1):
    if s['type']=='vo':
        with wave.open(str(P/'assets/vo'/f'{i:02d}_{s["name"]}_raw.wav')) as w:vo+=w.getnframes()/w.getframerate()
result=dict(probe=probe(final),segments=segments,shot_samples=len(frames),narration_seconds=vo,first_insert_start=next(x['start'] for x in segments if x['type']=='insert'),added_captions=cfg['captions']['enabled'])
(Q/'measurements.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='probe'},indent=2))
