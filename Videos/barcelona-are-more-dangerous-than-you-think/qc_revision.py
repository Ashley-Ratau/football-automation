import json,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent; out=P/'_tmp/revision_v2/qc';out.mkdir(parents=True,exist_ok=True)
cfg=json.loads((P/'long_form_project.json').read_text())
master=P/'final video'/cfg['output_filename']; prior=P/'versions/v1'/cfg['output_filename']
def call(args):return subprocess.run(args,capture_output=True,text=True,check=True).stdout.strip()
audio=[]
for file in [prior,master]:audio.append(call(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']))
probe=json.loads(call(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(master)]))
rows=[]; offset=0
for i,s in enumerate(cfg['sections'],1):
    local=0
    for shot in s['broll']:
        if 'tactics_' in shot['file']:rows.append((offset+local+shot['duration']/2,s['name'],shot))
        local+=shot['duration']
    seg=P/'_tmp/revision_v2'/f'segment_{i:02d}_{s["name"]}.mp4'
    if not seg.exists():seg=P/'_tmp'/seg.name
    offset+=float(call(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(seg)]))
def grab(pair):
    i,(t,section,shot)=pair;f=out/f'tactic_{i:02d}.jpg'
    call(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(master),'-frames:v','1','-vf','scale=480:270',str(f)])
    return f
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(grab,enumerate(rows)))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for first in range(0,len(rows),12):
    im=Image.new('RGB',(1440,1280),'#0a1420');d=ImageDraw.Draw(im)
    for j,f in enumerate(files[first:first+12]):
        x=j%3*480;y=j//3*320
        with Image.open(f) as pic:im.paste(pic,(x,y))
        t,section,shot=rows[first+j];d.text((x+5,y+275),f'{t:.1f}s {section}\n{shot["narration_anchor"]}',font=font,fill='white')
    im.save(out/f'contact_{first//12+1:02d}.jpg',quality=92)
report={'audio_packet_hashes':audio,'audio_identical':audio[0]==audio[1],'duration':probe['format']['duration'],'streams':[{k:s.get(k) for k in ['codec_type','codec_name','width','height','r_frame_rate']} for s in probe['streams']],'tactical_shots':len(rows),'distinct_tactical_assets':len(set(r[2]['file'] for r in rows))}
(P/'final video/revision_v2_qc.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert report['audio_identical']
