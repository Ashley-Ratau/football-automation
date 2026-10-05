import argparse,json,shutil
from pathlib import Path
import build_barcelona as b
P=b.P;A=b.A
cfg=A.load_config(P)
video=Path(r'C:\Users\Wendy\Downloads\barcelona danger.mp4')
thumb=Path(r'C:\Users\Wendy\Downloads\Generated Image September 19, 2026 - 12_31PM.jpg')
cfg['output_filename']='barcelona-user-edited.mp4'
cfg['thumbnail']='assets/thumbnail/user_upscaled.jpg'
cfg['upload']['privacy']='private'
shutil.copy2(video,P/'final video'/cfg['output_filename'])
shutil.copy2(thumb,P/cfg['thumbnail'])
(P/'user_edit_upload_config.json').write_text(json.dumps(cfg,indent=2))
A.load_config=lambda project:cfg
args=argparse.Namespace(project=str(P),confirm_upload=True)
A.prepare_upload(args)
A.upload_project(args)
