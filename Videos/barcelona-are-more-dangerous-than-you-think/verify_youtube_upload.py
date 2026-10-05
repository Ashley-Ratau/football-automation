import sys,json,datetime
from pathlib import Path
sys.path.insert(0,r'C:\Users\Wendy\Documents\Football Channel\work')
import youtube_oauth_tool as y
P=Path(__file__).resolve().parent
r=y.youtube_service().videos().list(part='snippet,status,contentDetails,processingDetails',id='Erw0uVgX_Ic').execute()
(P/'final video/upload records').mkdir(exist_ok=True)
(P/'final video/upload records/verification.json').write_text(json.dumps(r,indent=2))
for v in r.get('items',[]):
 print(json.dumps({k:v.get(k) for k in ['id','status','contentDetails','processingDetails']},indent=2))
