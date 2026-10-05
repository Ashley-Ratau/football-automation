from pathlib import Path
import subprocess,json
root=Path(r'C:\Users\Wendy\Documents\Football Channel\Videos\the-raphinha-experiment-will-break-la-liga');out=root/'assets/broll_contact_sheets';out.mkdir(exist_ok=True)
manifest=[]
for p in (root/'assets/broll').glob('*.mp4'):
 j=p.with_suffix('.info.json')
 if not j.exists():continue
 m=json.loads(j.read_text(encoding='utf-8'));d=float(m['duration']);step=d/30
 sheet=out/f'{p.stem}.jpg'
 if not sheet.exists():
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-y','-i',str(p),'-vf',f'fps=1/{step},scale=320:180,tile=5x6','-frames:v','1',str(sheet)],check=True)
 manifest.append({'file':str(p),'url':m.get('webpage_url'),'upload_date':m.get('upload_date'),'title':m.get('title'),'channel':m.get('channel'),'duration':d,'width':m.get('width'),'height':m.get('height'),'vcodec':m.get('vcodec'),'contact_sheet':str(sheet),'sheet_times_note':f'row-major 30cells, centers approximately (index+0.5)*{step:.3f} seconds','status':'await visual QC'})
(root/'assets/broll_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8');print('Catalogued',len(manifest))
