import json
import build_barcelona as b
P=b.P; A=b.A
A.ffmpeg_exe=lambda:'ffmpeg'
cfg=A.load_config(P)
paths=[]
for idx,s in enumerate(cfg['sections'],1):
    output=P/'_tmp'/f'segment_{idx:02d}_{s["name"]}.mp4'
    if idx in [1,4,5,7,11]:
        A.render_vo_section(P,s,idx,output,cfg['settings'],'eleven_multilingual_v2',True)
    paths.append(output)
concat=P/'_tmp/segments_concat.txt'
concat.write_text('\n'.join("file '"+x.as_posix()+"'" for x in paths))
b.invoke(['ffmpeg','-y','-f','concat','-safe','0','-i',concat,'-c','copy','-movflags','+faststart',P/'_tmp/assembled_no_music.mp4'])
print('Repairs assembled',flush=True)
