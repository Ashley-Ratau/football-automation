"""Rebuild changed visuals while preserving approved section audio and frame counts."""
from pathlib import Path
import json,subprocess,sys,shutil
import build_raphinha as B
P=Path(__file__).resolve().parent
cfg=json.loads((P/'long_form_project.json').read_text())
selected=set(sys.argv[1:]);settings=cfg['settings']
for index,s in enumerate(cfg['sections'],1):
    if s['name'] not in selected:continue
    segment=P/'_tmp'/f'segment_{index:02d}_{s["name"]}.mp4'
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(segment)]))
    frames=int(next(x['nb_frames'] for x in p['streams'] if x['codec_type']=='video'))
    duration=B.A.media_probe(P/'_tmp'/f'{index:02d}_{s["name"]}_voice.aac')['duration']
    visual=P/'_tmp'/f'{index:02d}_{s["name"]}_visual.mp4'
    B.visual(P,s,duration,visual,settings)
    revised=segment.with_name(segment.stem+'_revision.mp4')
    B.invoke(['ffmpeg','-y','-i',visual,'-i',segment,'-map','0:v:0','-map','1:a:0','-frames:v',frames,'-c','copy','-movflags','+faststart',revised])
    revised.replace(segment)
assembled=P/'_tmp/assembled_no_music.mp4'
B.invoke(['ffmpeg','-y','-f','concat','-safe','0','-i',P/'_tmp/segments_concat.txt','-c','copy','-movflags','+faststart',assembled])
final=P/'final video'/cfg['output_filename']
B.music(assembled,P/cfg['music_bed'],final,settings)
report=json.loads((P/'final video/build_report.json').read_text())
report['probe']=B.A.media_probe(final)
report['visual_revision_sections']=sorted(selected)
(P/'final video/build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Visual correction complete',sorted(selected),flush=True)
