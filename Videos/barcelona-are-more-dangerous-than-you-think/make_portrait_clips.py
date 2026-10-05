from pathlib import Path
import subprocess,concurrent.futures
P=Path(__file__).resolve().parent
FF=r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
def make(name):
    src=P/'assets/thumbnail/references'/f'{name}_official_portrait.png'
    dst=P/'assets/broll'/f'portrait_{name}.mp4'
    graph='[1:v]format=rgba,scale=-1:1400[p];[0:v][p]overlay=x=(W-w)/2:y=-20-2*t:shortest=1,format=yuv420p[v]'
    r=subprocess.run([FF,'-y','-f','lavfi','-i','color=c=0x070e1c:s=1920x1080:r=30:d=10','-loop','1','-i',str(src),'-filter_complex',graph,'-map','[v]','-t','10','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',str(dst)],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-2000:])
    print(dst.name,flush=True)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(make,['lamine_yamal','raphinha','pedri']))
