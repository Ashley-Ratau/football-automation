"""Rebuild only changed visual sections; preserve approved master audio bit-for-bit."""
import json
import build_barcelona as b
P=b.P; A=b.A; A.ffmpeg_exe=lambda:'ffmpeg'
cfg=A.load_config(P)
old=json.loads((P/'versions/v1/long_form_project.json').read_text())
tmp=P/'_tmp/revision_v2';tmp.mkdir(exist_ok=True)
paths=[];changed=[]
for i,(s,prior) in enumerate(zip(cfg['sections'],old['sections']),1):
    original=P/'_tmp'/f'segment_{i:02d}_{s["name"]}.mp4'
    if s['broll']==prior['broll']:
        paths.append(original);continue
    changed.append(s['name'])
    visual=P/'_tmp'/f'{i:02d}_{s["name"]}_visual.mp4'
    duration=A.media_probe(original)['duration']
    frames=int(b.invoke(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','default=nw=1:nk=1',original]).stdout.strip())
    b.visual(P,s,duration,visual,cfg['settings'])
    output=tmp/f'segment_{i:02d}_{s["name"]}.mp4'
    b.invoke(['ffmpeg','-v','error','-y','-i',visual,'-i',original,'-map','0:v:0','-map','1:a:0','-frames:v',frames,'-t',duration,'-c','copy',output])
    paths.append(output)
concat=tmp/'concat.txt';concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in paths))
assembled=tmp/'visual_assembled.mp4'
b.invoke(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',concat,'-c','copy',assembled])
approved=P/'versions/v1/barcelona-are-more-dangerous-than-you-think.mp4'
output=P/'final video'/cfg['output_filename']
b.invoke(['ffmpeg','-v','error','-y','-i',assembled,'-i',approved,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output])
probe=A.media_probe(output)
report={'changed_sections':changed,'probe':probe,'audio':'Copied without re-encoding from approved v1 master','captions':False}
(P/'final video/revision_v2_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
