from pathlib import Path
import json,hashlib,base64,subprocess,concurrent.futures,time,requests
P=Path(__file__).resolve().parents[1]
sections=json.loads((P/'long_form_project.json').read_text(encoding='utf-8'))['sections']
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
