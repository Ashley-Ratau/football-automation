from pathlib import Path
import re,json,hashlib,base64,subprocess,concurrent.futures,time
import requests

P=Path(__file__).resolve().parents[1]
script=(P/'03 script.md').read_text(encoding='utf-8-sig').split('\n---')[0]
chapters=re.split(r'## \d\d[^\n]*\n',script)[1:]
def clean(t):
    return re.sub(r'\s+',' ',re.sub(r'\[INSERT[^\]]*\]','',t)).strip()
c3=chapters[2].split('[INSERT 2:')
c4=chapters[3].split('[INSERT 3:')
parts=[('hook',clean(chapters[0])),('season',clean(chapters[1])),('cas_setup',clean(c3[0])),('cas_followup',clean(c3[1].split(']',1)[1])),('money',clean(c4[0])),('warning_meaning',clean(c4[1].split(']',1)[1])),('respect',clean(chapters[4])),('parade',clean(chapters[5])),('findings',clean(chapters[6])),('ending',clean(chapters[7]))]
# The newer interview is represented by attributed narration; no downloaded original was accessible.
parts[7]=(parts[7][0],parts[7][1].replace('It was funny because supporters understood the history.','He said that if it happened, he would book a flight, buy the beer, and hold a parade in his garden. Supporters immediately understood the joke.'))
parts[0]=(parts[0][0],parts[0][1].replace('Then Klopp explained what he believed made this rivalry different.','Years later, Klopp put the problem into words.'))
sections=[]
for name,text in parts:
    if name=='hook': sections.append({'type':'insert','name':'cold_open','file':'assets/inserts/warning.mp4','start':0,'end':13.6})
    sections.append({'type':'vo','name':name,'text':text,'broll':[],'pause_after_seconds':0.15})
    if name=='cas_setup': sections.append({'type':'insert','name':'cas_interview','file':'assets/inserts/cas.mp4','start':0,'end':25})
    if name=='money': sections.append({'type':'insert','name':'financial_ceiling','file':'assets/inserts/ceiling.mp4','start':0,'end':24})
config=json.loads((P/'long_form_project.json').read_text(encoding='utf-8-sig'))
config['music_bed']=''
config['settings'].update(voice_speed=1.15,voice_gain_db=0,broll_clip_max_seconds=600,insert_fade_seconds=0.12)
config['sections']=sections
(P/'long_form_project.json').write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding='utf-8')
(P/'production'/'narration.txt').write_text('\n\n'.join(f'{n}\n{t}' for n,t in parts),encoding='utf-8')

def env_vars():
    env={}
    for line in Path(r'C:\Users\Wendy\Documents\Football Channel\work\secrets\.env.local').read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    return env
key=env_vars().get('ELEVENLABS_API_KEY')
voice='bu5eKETbFKC8G702EAU4'
def generate(job):
    i,s=job; stem=f"{i:02d}_{s['name']}"; raw=P/'assets'/'vo'/f'{stem}_raw.mp3'; wav=raw.with_suffix('.wav'); meta=raw.with_suffix('.json')
    digest=hashlib.sha256(s['text'].encode()).hexdigest()
    if not (raw.exists() and meta.exists() and json.loads(meta.read_text())['script_sha256']==digest):
        payload={'text':s['text'],'model_id':'eleven_multilingual_v2','voice_settings':{'stability':.43,'similarity_boost':.82,'style':.18,'use_speaker_boost':True}}
        for attempt in range(3):
            response=requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps',params={'output_format':'mp3_44100_192'},headers={'xi-api-key':key,'Content-Type':'application/json'},json=payload,timeout=180)
            if response.status_code==200: break
            if response.status_code in (429,500,502,503): time.sleep(2+attempt*3);continue
            raise RuntimeError(f"TTS {stem}: HTTP {response.status_code}")
        response.raise_for_status(); data=response.json(); raw.write_bytes(base64.b64decode(data.pop('audio_base64')))
        data.update(script_sha256=digest,text=s['text'],voice_id=voice,model_id='eleven_multilingual_v2')
        meta.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    # Match Liam's pacing in the existing renderer; normalize without clipping.
    subprocess.run(['ffmpeg','-y','-loglevel','error','-threads','2','-i',str(raw),'-af','loudnorm=I=-16:TP=-2:LRA=9','-ac','2','-ar','44100',str(wav)],check=True)
    print(f"VO ready {stem}",flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(generate,[(i,s) for i,s in enumerate(sections,1) if s['type']=='vo']))
print('Narration generated with Vinicius Liam voice; no music.',flush=True)
