"""Contact sheets (timestamped thumbnails) for shot selection."""
import subprocess, sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
FF=r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
if __import__('os').name != 'nt': FF = 'ffmpeg'  # cloud / Linux
def dur(f):
    p=subprocess.run([FF,'-i',str(f)],capture_output=True,text=True).stderr
    h,m,s=p.split('Duration: ')[1].split(',')[0].split(':'); return int(h)*3600+int(m)*60+float(s)
for f in sys.argv[2:]:
    f=Path(f); d=dur(f); step=float(sys.argv[1]); n=int(d//step)
    tmp=Path('_tmp/sheets')/(f.stem+'_%04d.jpg')
    subprocess.run([FF,'-y','-i',str(f),'-vf',f'fps=1/{step},scale=320:180','-q:v','4',str(tmp)],capture_output=True)
    ims=sorted(Path('_tmp/sheets').glob(f.stem+'_0*.jpg'))
    cols=8; rows=(len(ims)+cols-1)//cols
    sheet=Image.new('RGB',(cols*320,rows*180),'black'); d_=ImageDraw.Draw(sheet)
    for i,p in enumerate(ims):
        x,y=(i%cols)*320,(i//cols)*180; sheet.paste(Image.open(p),(x,y))
        d_.rectangle([x,y,x+70,y+24],fill='black'); d_.text((x+4,y+4),f'{i*step+step/2:.0f}s',fill='yellow',font=ImageFont.truetype('arial.ttf',18))
        p.unlink()
    sheet.save(f'_tmp/sheets/{f.stem}.jpg'); print(f.stem, round(d,1), len(ims))
