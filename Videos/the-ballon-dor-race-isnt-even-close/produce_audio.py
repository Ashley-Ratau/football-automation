"""ElevenLabs narration (Liam), original music cues and sound design for the Ballon d'Or video."""
from pathlib import Path
import base64, concurrent.futures, hashlib, json, subprocess, sys
import requests

P = Path(__file__).resolve().parent
SECRET = Path(r'C:\Users\Wendy\Documents\Football Channel\work\secrets\.env.local')
FF = r'C:\Users\Wendy\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
if __import__('os').name != 'nt': FF = 'ffmpeg'  # cloud / Linux
env = dict(x.strip().split('=', 1) for x in SECRET.read_text().splitlines() if '=' in x and not x.lstrip().startswith('#')) if SECRET.exists() else dict(__import__('os').environ)  # cloud: key from environment
KEY = env['ELEVENLABS_API_KEY'].strip().strip('"').strip("'")
HEADERS = {'xi-api-key': KEY, 'Content-Type': 'application/json'}
VOICE = 'bu5eKETbFKC8G702EAU4'

def wav(src, out):
    subprocess.run([FF, '-y', '-i', str(src), '-ar', '44100', '-ac', '2', '-c:a', 'pcm_s16le', str(out)], check=True, capture_output=True)

def speech(pair):
    i, s = pair
    out = P/'assets'/'vo'/f'{i:02d}_{s["name"]}_raw.wav'
    meta = out.with_suffix('.json')
    digest = hashlib.sha256(s['text'].encode()).hexdigest()
    if out.exists() and meta.exists() and json.loads(meta.read_text()).get('script_sha256') == digest:
        return f'Cached {s["name"]}'
    payload = {'text': s['text'], 'model_id': 'eleven_multilingual_v2',
        'voice_settings': {'stability': 0.40, 'similarity_boost': 0.82, 'style': 0.24, 'use_speaker_boost': True},
        'seed': 2600 + i}
    r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps',
        params={'output_format': 'mp3_44100_192'}, headers=HEADERS, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f'ElevenLabs {s["name"]}: HTTP {r.status_code}: {r.text[:250]}')
    d = r.json()
    mp3 = out.with_suffix('.mp3')
    mp3.write_bytes(base64.b64decode(d.pop('audio_base64')))
    wav(mp3, out)
    d.update(script_sha256=digest, voice_id=VOICE, model_id=payload['model_id'], text=s['text'])
    meta.write_text(json.dumps(d, indent=2), encoding='utf-8')
    return f'Generated {s["name"]}'

MUSIC = {
    'music_tension': 'Instrumental cinematic underscore for a football debate video, cold open. 90 BPM. Ticking muted percussion, low sub pulse, dark suspenseful synth drones, sparse piano stabs, building tension, room for a male narrator. No vocals, no crowd. Original composition.',
    'music_case': 'Instrumental confident hip-hop influenced football documentary underscore. 96 BPM. Punchy restrained drums, warm deep bass, modern Spanish guitar flourishes, dark synth pads, driving and assertive, room for a narrator. No vocals, no crowd. Original composition.',
    'music_verdict': 'Instrumental triumphant cinematic finale for a football analysis video. 100 BPM. Rising strings, big but restrained percussion, warm brass swells, emotional and victorious, room for a narrator, clean resolved ending. No vocals, no crowd. Original composition.',
}
SFX = {
    'hit': 'Deep cinematic impact boom hit, short, punchy, for a stat appearing on screen',
    'whoosh': 'Fast clean cinematic whoosh transition, short',
    'riser': 'Short tense cinematic riser building for two seconds, ending abruptly',
    'stamp': 'Heavy rubber stamp slamming on paper desk, single hit, crisp',
    'tick': 'Single clean mechanical ticker counter click',
    'crowd': 'Distant football stadium crowd roar swelling then fading',
}

def music(name, prompt, ms):
    out = P/'assets'/f'{name}.mp3'
    if out.exists(): return f'Cached {name}'
    r = requests.post('https://api.elevenlabs.io/v1/music', headers=HEADERS,
        json={'prompt': prompt, 'music_length_ms': ms, 'force_instrumental': True}, timeout=400)
    if r.status_code != 200: raise RuntimeError(f'Music {name} HTTP {r.status_code}: {r.text[:250]}')
    out.write_bytes(r.content); wav(out, out.with_suffix('.wav'))
    return f'Generated {name}'

def sfx(name, prompt):
    out = P/'assets'/'sfx'/f'{name}.mp3'
    if out.exists(): return f'Cached {name}'
    dur = 2.5 if name in ('riser',) else (5.0 if name == 'crowd' else 1.2)
    r = requests.post('https://api.elevenlabs.io/v1/sound-generation', headers=HEADERS,
        json={'text': prompt, 'duration_seconds': dur, 'prompt_influence': 0.6}, timeout=120)
    if r.status_code != 200: raise RuntimeError(f'SFX {name} HTTP {r.status_code}: {r.text[:250]}')
    out.write_bytes(r.content); wav(out, out.with_suffix('.wav'))
    return f'Generated {name}'

if __name__ == '__main__':
    sections = json.loads((P/'script_sections.json').read_text(encoding='utf-8'))
    jobs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        if '--vo' in sys.argv or len(sys.argv) == 1:
            jobs += [pool.submit(speech, p) for p in enumerate(sections, 1)]
        if '--music' in sys.argv or len(sys.argv) == 1:
            lens = {'music_tension': 60000, 'music_case': 180000, 'music_verdict': 90000}
            jobs += [pool.submit(music, n, p, lens[n]) for n, p in MUSIC.items()]
            jobs += [pool.submit(sfx, n, p) for n, p in SFX.items()]
        for j in jobs: print(j.result(), flush=True)
    (P/'assets'/'music_provenance.json').write_text(json.dumps({'provider': 'ElevenLabs Music + Sound Effects', 'music': MUSIC, 'sfx': SFX}, indent=2))
