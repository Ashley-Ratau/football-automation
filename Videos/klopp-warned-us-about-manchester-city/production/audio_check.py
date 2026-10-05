from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parents[1]
targets=[]
for f in sorted((P/'assets/vo').glob('*_raw.wav')):
    t=P/'_tmp'/(f.stem+'_listen.mp3')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-threads','2','-i',str(f),'-t','2.5','-af','atempo=1.15','-ar','22050','-ac','1','-b:a','48k',str(t)],check=True,capture_output=True);targets.append(t)
(P/'_tmp/vo_listen.txt').write_text('\n'.join("file '"+t.as_posix()+"'" for t in targets),encoding='utf-8')
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(P/'_tmp/vo_listen.txt'),'-c','copy',str(P/'_tmp/all_vo_listen.mp3')],check=True,capture_output=True)
print(f'Prepared {len(targets)} VO opening samples.')
