import json, subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
cfg = json.loads((P / 'long_form_project.json').read_text(encoding='utf-8-sig'))
report = json.loads((P / 'final video' / 'build_report.json').read_text(encoding='utf-8-sig'))
intervals=[]; offset=0.0
for rendered in report['timeline']:
    section=next(s for s in cfg['sections'] if s.get('name')==rendered['name'])
    dur=float(rendered['duration'])
    if section['type']=='vo':
        coverage=sum(float(x.get('duration',0)) for x in section.get('broll',[]))
        scale=dur/coverage
        local=0.0
        for item in section.get('broll',[]):
            d=float(item.get('duration',0))*scale
            if 'tactics_' not in str(item.get('file','')).replace('\\','/'):
                intervals.append((offset+local+0.02, offset+local+d-0.02))
            local += d
    offset += dur
merged=[]
for a,b in intervals:
    if merged and a-merged[-1][1] < 0.04: merged[-1]=(merged[-1][0],b)
    else: merged.append((a,b))
enable='+'.join(f'between(t,{a:.3f},{b:.3f})' for a,b in merged)
source=P/'final video'/'why-every-manchester-united-rebuild-fails-rebuilt.mp4'
out=P/'final video'/'why-every-manchester-united-rebuild-fails-rebuilt-polished.mp4'
graph=P/'edit'/'rebuilt_polish_filter.txt'; graph.parent.mkdir(exist_ok=True)
fg=("[0:v]split=2[base][flip];[flip]hflip[flipped];"
    f"[base][flipped]overlay=shortest=1:enable='{enable}',vignette=angle=PI/5,format=yuv420p[outv]")
graph.write_text(fg,encoding='utf-8')
subprocess.run(['ffmpeg','-y','-i',str(source),'-filter_complex_script',str(graph),'-map','[outv]','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','18','-c:a','copy','-movflags','+faststart',str(out)],check=True)
(P/'edit'/'rebuilt_mirror_windows.json').write_text(json.dumps({'windows':merged,'insert_sections':[s['name'] for s in cfg['sections'] if s['type']=='insert']},indent=2))
print(f'polished {out} with {len(merged)} live-action mirror windows')
