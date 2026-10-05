"""ElevenLabs narration (Liam) for each VO section. Music is NOT generated here (free library tracks instead)."""
from pathlib import Path
import base64, concurrent.futures, hashlib, json, subprocess
import requests
P = Path(__file__).resolve().parent
SECRET = Path(r'C:\Users\Wendy\Documents\Football Channel\work\secrets\.env.local')
FF = r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
if __import__('os').name != 'nt': FF = 'ffmpeg'  # cloud / Linux
env = dict(x.strip().split('=', 1) for x in SECRET.read_text().splitlines() if '=' in x and not x.lstrip().startswith('#')) if SECRET.exists() else dict(__import__('os').environ)  # cloud: key from environment
KEY = env['ELEVENLABS_API_KEY'].strip().strip('"').strip("'")
VOICE = 'c6SfcYrb2t09NHXiT80T'
SPEED = 1.15  # narration tempo (pitch kept); alignment times are rescaled to match

def retime(wav, d, k):
    """Speed the narration up by k (pitch preserved) from the original mp3 and rescale the timestamps."""
    if k == 1.0: return
    src = wav.with_suffix('.mp3'); total = SPEED if src.exists() else k
    subprocess.run([FF, '-y', '-i', str(src if src.exists() else wav), '-af', f'highpass=f=70,atempo={total},loudnorm=I=-16:TP=-1.5:LRA=7', '-ar', '44100', '-ac', '2', str(wav.with_suffix('.tmp.wav'))], check=True, capture_output=True)
    wav.with_suffix('.tmp.wav').replace(wav)
    for key in ('alignment', 'normalized_alignment'):
        al = d.get(key)
        if al:
            for f in ('character_start_times_seconds', 'character_end_times_seconds'): al[f] = [x / k for x in al[f]]

def speech(s):
    out = P/'assets'/'vo'/f'{s["name"]}.wav'; meta = out.with_suffix('.json')
    digest = hashlib.sha256(s['text'].encode()).hexdigest()
    if out.exists() and meta.exists():
        d = json.loads(meta.read_text(encoding='utf-8'))
        if d.get('script_sha256') == digest:
            if d.get('speed', 1.0) == SPEED: return f'cached {s["name"]}'
            retime(out, d, SPEED / d.get('speed', 1.0)); d['speed'] = SPEED; meta.write_text(json.dumps(d), encoding='utf-8')
            return f'retimed {s["name"]}'
    payload = {'text': s['text'], 'model_id': 'eleven_v4',
               'voice_settings': {'stability': 0.45, 'similarity_boost': 0.82, 'style': 0.15, 'use_speaker_boost': True}, 'seed': 77}
    r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps', params={'output_format': 'mp3_44100_192'},
                      headers={'xi-api-key': KEY, 'Content-Type': 'application/json'}, json=payload, timeout=180)
    if r.status_code != 200: raise RuntimeError(f'{s["name"]}: {r.status_code} {r.text[:200]}')
    d = r.json(); mp3 = out.with_suffix('.mp3'); mp3.write_bytes(base64.b64decode(d.pop('audio_base64')))
    subprocess.run([FF, '-y', '-i', str(mp3), '-af', 'highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=7', '-ar', '44100', '-ac', '2', str(out)], check=True, capture_output=True)
    retime(out, d, SPEED)
    d.update(script_sha256=digest, text=s['text'], speed=SPEED); meta.write_text(json.dumps(d), encoding='utf-8')
    return f'generated {s["name"]}'

if __name__ == '__main__':
    secs = [s for s in json.loads((P/'script.json').read_text(encoding='utf-8')) if s['type'] == 'vo']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(speech, secs): print(r, flush=True)
