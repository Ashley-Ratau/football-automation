"""Finalize already rendered sections without re-encoding their video."""
import json,shutil,time
import build_barcelona as b
P=b.P; A=b.A
A.ffmpeg_exe=lambda:'ffmpeg'
cfg=A.load_config(P)
source=P/'_tmp/assembled_no_music.mp4'
dest=P/'final video'/cfg['output_filename']
b.music(source,P/cfg['music_bed'],dest,cfg['settings'])
timeline=[]
for idx,s in enumerate(cfg['sections'],1):
    seg=P/'_tmp'/f'segment_{idx:02d}_{s["name"]}.mp4'
    timeline.append({'index':idx,'name':s['name'],'type':'vo','duration':A.media_probe(seg)['duration']})
probe=A.media_probe(dest)
ok=probe['has_audio'] and probe['has_video'] and probe['width']==1920 and probe['height']==1080 and 480<=probe['duration']<=600
A.extract_qc_frames(P,dest,timeline)
report={'project':str(P),'final_video':str(dest),'specs_ok':ok,'probe':probe,'timeline':timeline,'sound_effects':[],
 'captions_enabled':False,'captions_ass':'','qc_dir':str(P/'_tmp/qc'),'voice_model':'eleven_multilingual_v2','voice_id':'bu5eKETbFKC8G702EAU4',
 'built_at':time.strftime('%Y-%m-%dT%H:%M:%S'),'workflow':'Existing workspace automation with project-specific Liam audio and validated sentence shot list.'}
(P/'final video/build_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
if not ok:raise RuntimeError('Final master did not meet specification')
