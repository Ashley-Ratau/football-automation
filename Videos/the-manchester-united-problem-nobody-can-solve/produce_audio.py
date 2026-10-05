"""Project-specific ElevenLabs audio, consumed by the existing football pipeline."""
from pathlib import Path
import base64, concurrent.futures, hashlib, json, subprocess, sys, time
import requests

P = Path(__file__).resolve().parent
SECRET = Path(r'C:\Users\Wendy\Documents\Football Channel\work\secrets\.env.local')
FF = r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
env = dict(x.strip().split('=', 1) for x in SECRET.read_text().splitlines() if '=' in x and not x.lstrip().startswith('#'))
KEY = env['ELEVENLABS_API_KEY'].strip().strip('"').strip("'")
HEADERS = {'xi-api-key': KEY, 'Content-Type':'application/json'}
VOICE = 'bu5eKETbFKC8G702EAU4'

def speech(pair):
    i, s = pair
    out = P/'assets'/'vo'/f'{i:02d}_{s["name"]}_raw.wav'
    meta = out.with_suffix('.json')
    digest = hashlib.sha256(s['text'].encode()).hexdigest()
    if out.exists() and meta.exists() and json.loads(meta.read_text()).get('script_sha256') == digest:
        return f'Cached {s["name"]}'
    payload = {'text':s['text'], 'model_id':'eleven_multilingual_v2',
        'voice_settings':{'stability':0.43,'similarity_boost':0.82,'style':0.18,'use_speaker_boost':True},
        'seed':420+i}
    r=requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps',
        params={'output_format':'mp3_44100_192'},headers=HEADERS,json=payload,timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f'ElevenLabs {s["name"]}: HTTP {r.status_code}: {r.text[:250]}')
    d=r.json()
    mp3=out.with_suffix('.mp3')
    mp3.write_bytes(base64.b64decode(d.pop('audio_base64')))
    subprocess.run([FF,'-y','-i',str(mp3),'-ar','44100','-ac','2','-c:a','pcm_s16le',str(out)],check=True,capture_output=True)
    d.update(script_sha256=digest,voice_id=VOICE,model_id=payload['model_id'],text=s['text'])
    meta.write_text(json.dumps(d,indent=2),encoding='utf-8')
    return f'Generated {s["name"]}'

def music():
    out=P/'assets'/'music_original.mp3'
    if out.exists(): return
    prompt='Instrumental underscore for an intelligent high-energy football analysis documentary. 104 BPM. Tight restrained electronic percussion, deep warm pulse bass, dark atmospheric synth textures, subtle cinematic rising strings. Confident, suspenseful and forward moving. Space for a male narrator throughout. No vocals, no singing, no speech, no crowd samples, no massive drops. Smooth restrained intro and clean resolved ending. Original composition.'
    r=requests.post('https://api.elevenlabs.io/v1/music',headers=HEADERS,json={'prompt':prompt,'music_length_ms':120000,'force_instrumental':True},timeout=240)
    if r.status_code != 200: raise RuntimeError(f'Music HTTP {r.status_code}: {r.text[:250]}')
    out.write_bytes(r.content)
    (P/'assets'/'music_provenance.json').write_text(json.dumps({'provider':'ElevenLabs Music','prompt':prompt,'duration_ms':120000},indent=2))
    print('Generated original instrumental',flush=True)

if __name__=='__main__':
    if '--music' in sys.argv: music()
    else:
        cfg=json.loads((P/'long_form_project.json').read_text())
        pairs=[(i,s) for i,s in enumerate(cfg['sections'],1) if s['type']=='vo']
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for result in pool.map(speech,pairs): print(result,flush=True)
