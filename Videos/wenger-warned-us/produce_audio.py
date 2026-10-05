"""ElevenLabs narration (Liam) for each VO section. Music is NOT generated here (free library tracks instead)."""
from pathlib import Path
import base64, concurrent.futures, hashlib, json, subprocess
import requests
P = Path(__file__).resolve().parent
SECRET = Path(r'C:\Users\Wendy\Documents\Football Channel\work\secrets\.env.local')
FF = r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
env = dict(x.strip().split('=', 1) for x in SECRET.read_text().splitlines() if '=' in x and not x.lstrip().startswith('#'))
KEY = env['ELEVENLABS_API_KEY'].strip().strip('"').strip("'")
VOICE = 'bu5eKETbFKC8G702EAU4'

def speech(s):
    out = P/'assets'/'vo'/f'{s["name"]}.wav'; meta = out.with_suffix('.json')
    digest = hashlib.sha256(s['text'].encode()).hexdigest()
    if out.exists() and meta.exists() and json.loads(meta.read_text(encoding='utf-8')).get('script_sha256') == digest:
        return f'cached {s["name"]}'
    payload = {'text': s['text'], 'model_id': 'eleven_multilingual_v2',
               'voice_settings': {'stability': 0.45, 'similarity_boost': 0.82, 'style': 0.15, 'use_speaker_boost': True}, 'seed': 77}
    r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps', params={'output_format': 'mp3_44100_192'},
                      headers={'xi-api-key': KEY, 'Content-Type': 'application/json'}, json=payload, timeout=180)
    if r.status_code != 200: raise RuntimeError(f'{s["name"]}: {r.status_code} {r.text[:200]}')
    d = r.json(); mp3 = out.with_suffix('.mp3'); mp3.write_bytes(base64.b64decode(d.pop('audio_base64')))
    subprocess.run([FF, '-y', '-i', str(mp3), '-af', 'highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=7', '-ar', '44100', '-ac', '2', str(out)], check=True, capture_output=True)
    d.update(script_sha256=digest, text=s['text']); meta.write_text(json.dumps(d), encoding='utf-8')
    return f'generated {s["name"]}'

if __name__ == '__main__':
    secs = [s for s in json.loads((P/'script.json').read_text(encoding='utf-8')) if s['type'] == 'vo']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(speech, secs): print(r, flush=True)
