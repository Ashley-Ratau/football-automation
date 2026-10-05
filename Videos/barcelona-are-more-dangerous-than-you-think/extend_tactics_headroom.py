"""Append 1.2 seconds of final-pose headroom without re-encoding existing frames."""
from pathlib import Path
import subprocess,json,shutil
import cv2,imageio_ffmpeg
P=Path(__file__).resolve().parent;Q=P/'_tmp/tactics_v2_qa/headroom';Q.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe()
def run(args):
 r=subprocess.run([FF,'-hide_banner','-loglevel','error',*map(str,args)],capture_output=True)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
 return r.stdout
checks=[]
for x in json.loads((P/'tactics_v2_mapping.json').read_text()).values():
 src=P/x['file'];cap=cv2.VideoCapture(str(src));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));cap.set(cv2.CAP_PROP_POS_FRAMES,n-1);ok,fr=cap.read();cap.release();assert ok
 if n/30 >= x['duration']+1.1:continue
 backup=Q/src.name;shutil.copy2(src,backup)
 tail=Q/(src.stem+'_tail.mp4');out=Q/(src.stem+'_extended.mp4')
 cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(tail)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for _ in range(36):proc.stdin.write(fr.tobytes())
 proc.stdin.close();assert proc.wait()==0
 listing=Q/(src.stem+'_concat.txt');listing.write_text("file '"+backup.as_posix()+"'\nfile '"+tail.as_posix()+"'\n")
 run(['-y','-f','concat','-safe','0','-i',listing,'-c','copy','-movflags','+faststart',out])
 # Ignore timestamp columns and compare every decoded pixel hash of the original frames.
 def hashes(path):return [l.split(',')[-1].strip() for l in run(['-i',path,'-frames:v',n,'-f','framemd5','-']).decode().splitlines() if not l.startswith('#')]
 assert hashes(backup)==hashes(out),src.name+' altered original pixels'
 shutil.copy2(out,src);checks.append({'file':src.name,'original_frames':n,'tail_frames':36,'original_decoded_pixels_identical':True})
 print(src.name,flush=True)
(Q/'pixel_preservation.json').write_text(json.dumps(checks,indent=2));print('Extended',len(checks),flush=True)
