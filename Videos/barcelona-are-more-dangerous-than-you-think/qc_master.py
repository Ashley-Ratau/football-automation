"""Technical and visual evidence for the delivered master."""
from pathlib import Path
import concurrent.futures,json,subprocess
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
FF=r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
F=P/'final video'/'barcelona-are-more-dangerous-than-you-think.mp4'
OUT=P/'_tmp'/'qc_full';OUT.mkdir(parents=True,exist_ok=True)

def main():
    shots=json.loads((P/'shot_timeline.json').read_text())
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    def grab(pair):
        i,s=pair;t=s['timeline_start']+s['duration']/2
        o=OUT/f'shot_{i:03d}.jpg'
        subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=384:216',str(o)],check=True,capture_output=True)
        return o
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: pics=list(pool.map(grab,enumerate(shots)))
    for j in range(0,len(pics),20):
        sheet=Image.new('RGB',(1536,1250),'#101722');d=ImageDraw.Draw(sheet)
        for k,pic in enumerate(pics[j:j+20]):
            x=k%4*384;y=k//4*250
            with Image.open(pic) as im:sheet.paste(im,(x,y))
            s=shots[j+k]
            label=f'{j+k+1:03d} {s["timeline_start"]:.1f}s / {s["duration"]:.2f}s {Path(s["file"]).stem}'
            d.text((x+5,y+219),label,fill='white',font=font)
        sheet.save(OUT/f'contact_{j//20+1:02d}.jpg',quality=92)
    checks={}
    cmd=[FF,'-hide_banner','-threads','2','-i',str(F),'-vf','blackdetect=d=0.15:pix_th=0.08,freezedetect=n=-55dB:d=2.5',
        '-af','ebur128=peak=true','-f','null','NUL']
    r=subprocess.run(cmd,capture_output=True,text=True)
    (OUT/'signal_analysis.log').write_text(r.stderr)
    checks['signal_analysis_exit']=r.returncode
    checks.update(shots=len(shots),max_shot=max(s['duration'] for s in shots),min_shot=min(s['duration'] for s in shots),mean_shot=sum(s['duration'] for s in shots)/len(shots))
    (OUT/'technical_qc.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
