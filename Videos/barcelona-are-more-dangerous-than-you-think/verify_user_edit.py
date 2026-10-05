import sys,json
from pathlib import Path
sys.path.insert(0,r'C:\Users\Wendy\Documents\Football Channel\work')
import youtube_oauth_tool as y
P=Path(__file__).resolve().parent
r=y.youtube_service().videos().list(part='snippet,status,contentDetails,processingDetails',id='6J6IGowiuBk').execute()
(P/'final video/upload records/user_edit_verification.json').write_text(json.dumps(r,indent=2))
for v in r.get('items',[]):
 c=v.get('contentDetails',{})
 print(json.dumps({'id':v['id'],'title':v['snippet']['title'],'status':v.get('status'),'duration':c.get('duration'),'hasCustomThumbnail':c.get('hasCustomThumbnail'),'blocked_regions':len(c.get('regionRestriction',{}).get('blocked',[])),'processing':v.get('processingDetails')},indent=2))
