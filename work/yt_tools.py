"""Small YouTube Data API helpers: set thumbnail, check processing / restriction status.
Usage:  python work/yt_tools.py thumb <video_id> <image.jpg>
        python work/yt_tools.py status <video_id>
"""
import json, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
TOKEN = json.loads((ROOT/'secrets'/'youtube_token_youtube_only.json').read_text())
CLIENT = json.loads((ROOT/'secrets'/'youtube_oauth_client.json').read_text())
CLIENT = CLIENT.get('installed') or CLIENT.get('web')

def access_token():
    r = requests.post('https://oauth2.googleapis.com/token', data=dict(client_id=CLIENT['client_id'], client_secret=CLIENT['client_secret'],
                      refresh_token=TOKEN['refresh_token'], grant_type='refresh_token'), timeout=60)
    r.raise_for_status(); return r.json()['access_token']

def thumb(vid, img):
    r = requests.post(f'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}',
                      headers={'Authorization': f'Bearer {access_token()}', 'Content-Type': 'image/jpeg'}, data=Path(img).read_bytes(), timeout=120)
    print(r.status_code, r.text[:400])

def status(vid):
    r = requests.get('https://www.googleapis.com/youtube/v3/videos', params=dict(id=vid, part='status,processingDetails,contentDetails,snippet'),
                     headers={'Authorization': f'Bearer {access_token()}'}, timeout=60)
    items = r.json().get('items', [])
    if not items: print('NOT FOUND', r.text[:300]); return
    v = items[0]
    print(json.dumps(dict(title=v['snippet']['title'], status=v['status'], processing=v.get('processingDetails'),
                          regionRestriction=v['contentDetails'].get('regionRestriction'), contentRating=v['contentDetails'].get('contentRating'),
                          duration=v['contentDetails'].get('duration')), indent=1))

if __name__ == '__main__':
    {'thumb': lambda: thumb(sys.argv[2], sys.argv[3]), 'status': lambda: status(sys.argv[2])}[sys.argv[1]]()
