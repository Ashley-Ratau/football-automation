from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
root=Path(r'C:\Users\Wendy\Documents\Football Channel\Videos\barcelona-are-more-dangerous-than-you-think')
broll=root/'assets/broll';out=root/'assets/broll_contact_sheets';out.mkdir(exist_ok=True)
manifest=[]
for p in broll.glob('*.mp4'):
    info_path=p.with_suffix('.info.json')
    if not info_path.exists():continue
    meta=json.loads(info_path.read_text(encoding='utf-8'))
    duration=float(meta.get('duration',0));ts=[round((i+0.5)*duration/20,1) for i in range(20)]
    sheet=Image.new('RGB',(1280,800),'#121212');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(ts if not (out/f'{p.stem}.jpg').exists() else []):
        frame=out/f'{p.stem}_{t}.jpg'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=320:180',str(frame)],check=True)
        with Image.open(frame) as im:sheet.paste(im,(i%4*320,i//4*160)) if False else None
        with Image.open(frame) as im:sheet.paste(im.resize((320,140)),(i%4*320,i//4*160))
        draw.text((i%4*320+6,i//4*160+142),f'{t:.1f}s',fill='white')
        frame.unlink()
    if not (out/f'{p.stem}.jpg').exists():sheet.save(out/f'{p.stem}.jpg',quality=91)
    manifest.append({'file':str(p),'url':meta.get('webpage_url'),'title':meta.get('title'),'upload_date':meta.get('upload_date'),'channel':meta.get('channel'),'duration':duration,'width':meta.get('width'),'height':meta.get('height'),'vcodec':meta.get('vcodec'),'archive':None,'verification':'Upload metadata captured; visual match verification required before exact-match use','contact_sheet':str(out/f'{p.stem}.jpg')})
(root/'assets/broll_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print('Catalogued',len(manifest),'sources')


