"""Build 'Wenger Knew' — quote-driven documentary.

Timeline = script.json in order: VO sections (ElevenLabs), real soundbites (clip audio + video,
optional cutaways), quote cards. Visual shots inside VO sections start on narration words.
"""
from pathlib import Path
import json, wave, subprocess, hashlib, concurrent.futures, sys
import numpy as np
import gfx as G, quotes as Q

P = Path(__file__).resolve().parent
FF = G.FF; FPS = 30; SR = 44100
CL = P/'_tmp'/'clips'; CL.mkdir(parents=True, exist_ok=True)
SCRIPT = json.loads((P/'script.json').read_text(encoding='utf-8'))

def hd(i): return f'assets/clips/hd/{i}.mp4'
def br(n): return f'assets/broll/{n}.mp4'
FAREWELL, TOUCH, SKYFA, ETIHAD, ITV, TIFO = br('wenger_farewell'), br('wenger_touchline'), br('sky_fa_statement_2026'), br('etihad_deal_2011'), br('itv_uefa_ban_2020'), br('tifo_football_leaks')
QPR, TROPHY18, APPEAL, CITYARS = br('city_qpr_2012'), br('city_trophy_2018'), br('sky_city_appeal'), hd('DQwS2cONShU')

def S(f, s, **o): return dict(file=f, start=s, **o)
K = G.kinetic

PLAN = {
 'cold_open': [
  ('On the twenty-ninth', S(SKYFA, 43)),
  ('an independent commission', S(SKYFA, 103)),
  ('sham sponsorship', S(SKYFA, 130)),
  ('More than nine hundred', S(SKYFA, 118, txt=K('£900,000,000+', size=150))),
  ('From two thousand', S(TROPHY18, 34, txt=K('2009/10 — 2017/18', size=130))),
  ('The last nine seasons', S(TOUCH, 2)),
  ('losing players to City', S(CITYARS, 43)),
  ('losing ground to City', S(TROPHY18, 10)),
  ('warning anyone', S(hd('c0xtseSCR00'), 36)),
  ('Almost nobody did', S(FAREWELL, 163, slow=True)),
 ],
 'the_principle': [
  ('To understand', S(FAREWELL, 50)),
  ('go back to the day', S(hd('ZpEhdXY5Wqk'), 20, bw=True)),
  ('Arsenal unveil', S(hd('ZpEhdXY5Wqk'), 27, bw=True)),
 ],
 'the_squeeze': [
  ('For ten years', S(TOUCH, 22)),
  ('Three league titles', S(TOUCH, 26)),
  ('The Invincibles', S(FAREWELL, 586)),
  ('They borrowed', S(FAREWELL, 14)),
  ('tightened the budget', S(FAREWELL, 78)),
  ('In his own words', S(hd('_OdfMfFX9zU'), 28)),
 ],
 'takeover': [
  ('September two thousand', S(SKYFA, 126)),
  ('Abu Dhabi buys', S(SKYFA, 150)),
  ('Within a year', S(SKYFA, 107)),
  ('July two thousand', S(CITYARS, 38)),
  ('Kolo Touré', S(hd('eTWuCyg9CAo'), 3, bw=True)),
  ('Two months later', S(CITYARS, 282)),
  ('sprints the length', S(CITYARS, 293)),
  ('who used to sing', S(CITYARS, 34)),
  ('Wenger is asked', S(hd('tn4NzUlINPU'), 0, bw=True)),
 ],
 'etihad': [
  ('But by twenty eleven', S(ETIHAD, 82)),
  ('That July', S(ETIHAD, 18)),
  ('the airline of', S(ETIHAD, 114)),
  ('Shirt, stadium', S(ETIHAD, 66)),
  ('Reported at around', S(ETIHAD, 58, txt=K('£400 MILLION', sub='reported value · 10 years'))),
  ('Wenger was asked', S(TOUCH, 6)),
  ('exactly what the commission', S(TOUCH, 38)),
 ],
 'nasri': [
  ('Read that again', S(ETIHAD, 90)),
  ('Sponsorship at the market', S(ETIHAD, 94, txt=K('“AT THE MARKET PRICE”', size=120))),
  ('That is the heart', S(SKYFA, 44)),
  ('Deals that looked', S(SKYFA, 134)),
  ('And the same summer', S(TOUCH, 34)),
  ('Gaël Clichy', S(CITYARS, 46)),
  ('Then Samir Nasri', S(hd('nxAdOBK3Jcs'), 2, bw=True)),
  ('a few days after', S(hd('A0h3HYIKkJg'), 12, bw=True)),
 ],
 'titles': [
  ('Nine months later', S(QPR, 1376)),
  ('Their first league', S(QPR, 1418)),
  ('with Nasri and Clichy', S(QPR, 1442)),
  ('They won it again', S(TROPHY18, 22)),
  ('the summer Bacary', S(hd('8IdB-Xx4eHY'), 30)),
  ('And again in twenty eighteen', S(TROPHY18, 26)),
  ('with a hundred points', S(TROPHY18, 70, txt=K('100 POINTS', size=150))),
  ('Every one of those', S(TROPHY18, 86)),
  ('In those same nine', S(TOUCH, 2, bw=True)),
  ('Arsenal did not win', S(TOUCH, 34, bw=True, txt=K('ARSENAL LEAGUE TITLES: 0', size=110, color=G.RED))),
  ('And by December', S(hd('c0xtseSCR00'), 20)),
 ],
 'united': [
  ('A month later', S(hd('1lOYBduFs0g'), 0)),
  ('Wenger was asked', S(hd('1lOYBduFs0g'), 40)),
  ('Listen to which', S(hd('1lOYBduFs0g'), 90)),
 ],
 'united_2': [
  ('He praised', S(hd('1lOYBduFs0g'), 100)),
  ('He did not say', S(SKYFA, 138, slow=True)),
 ],
 'leaks': [
  ('In May twenty eighteen', S(FAREWELL, 410)),
  ('Wenger left Arsenal', S(FAREWELL, 530)),
  ('Six months later', S(TIFO, 172)),
  ('suggesting that money', S(TIFO, 186)),
  ('In February twenty twenty', S(ITV, 18)),
  ('UEFA banned City', S(ITV, 23)),
  ('for two seasons', S(ITV, 35)),
  ('Wenger was asked about it', S(hd('ZKu4Bgdscz8'), 0)),
 ],
 'cas': [
  ('Five months later', S(ITV, 42)),
  ('The Court of Arbitration', S(ITV, 46, txt=K('BAN OVERTURNED', size=150))),
  ('Some of the allegations', S(ITV, 62)),
  ('City paid a fine', S(ITV, 110)),
  ('Jürgen Klopp', S(hd('dCbEdL2fEDc'), 20)),
 ],
 'cas_2': [('Pep Guardiola', S(ITV, 114))],
 'verdict': [
  ('The people said', S(SKYFA, 106)),
  ('In February twenty twenty-three', S(SKYFA, 114)),
  ('A hundred and fifteen', S(SKYFA, 119, txt=K('115 CHARGES', size=160))),
  ('And three and a half', S(SKYFA, 3)),
  ('found City guilty', S(SKYFA, 46)),
  ('Sham contracts', S(SKYFA, 127)),
  ('Revenues inflated', S(SKYFA, 146)),
  ('concerted efforts', S(SKYFA, 122, txt=K('“CONCERTED EFFORTS TO STOP AND FRUSTRATE', size=74, sub='THE INVESTIGATION” — Premier League statement'))),
 ],
 'fair': [
  ('Now, to be fair', S(APPEAL, 8)),
  ('City deny', S(APPEAL, 34)),
  ('The punishment has not', S(APPEAL, 46)),
  ('But whatever happens', S(FAREWELL, 362, slow=True)),
  ('the man who spent', S(FAREWELL, 510, slow=True)),
 ],
 'ending': [
  ('He lost his players', S(CITYARS, 294, bw=True)),
  ('He lost the title races', S(TROPHY18, 34, bw=True)),
  ('For years, he was told', S(TOUCH, 6, bw=True)),
  ('And all along', S(FAREWELL, 418)),
  ('He said it in nineteen', S(hd('ZpEhdXY5Wqk'), 10, bw=True)),
  ('He said it in twenty eleven', S(ETIHAD, 82, bw=True)),
  ('He said it again', S(hd('ZKu4Bgdscz8'), 2)),
 ],
 'outro': [
  ('Arsène Wenger tried', S(FAREWELL, 550, slow=True)),
  ('Almost nobody', S(FAREWELL, 366, slow=True)),
 ],
}
# cutaways inside long soundbites: (offset seconds into the quote, shot)
CUTAWAYS = {
 'q_cheats': [(7.5, S(TROPHY18, 40, bw=True)), (12.5, S(hd('_Ej9w-zFyHI'), 20, bw=True, keep_audio_time=True))],
 'q_squeeze': [(8.5, S(FAREWELL, 14)), (13.0, S(SKYFA, 150)), (19.0, S(CITYARS, 46)), (23.0, S(TOUCH, 30))],
 'q_former_players': [(6.5, S(CITYARS, 38))],
 'q_rules': [(8.0, S(ITV, 18))],
 'q_punished': [(7.0, S(SKYFA, 130)), (12.0, S(ITV, 26))],
}
NOCAP = {'dCbEdL2fEDc'}  # source already has burned-in subtitles
OLD = {'ZpEhdXY5Wqk', 'eTWuCyg9CAo', 'nxAdOBK3Jcs', 'A0h3HYIKkJg', 'tn4NzUlINPU', '9fhK0b4G3Xw', '_Ej9w-zFyHI'}

def wav_read(path):
    with wave.open(str(path)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels())
def wav_write(path, a):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())

def vo_meta(name): return json.loads((P/'assets'/'vo'/f'{name}.json').read_text(encoding='utf-8'))
def anchor_time(meta, anchor, after):
    al = meta['alignment']; ch = ''.join(al['characters']); k = ch.find(anchor, after)
    if k < 0: raise KeyError(f'anchor {anchor!r}')
    return al['character_start_times_seconds'][k], k + 1

def vo_words(meta, t0):
    al = meta['alignment']; out, cur, cs, pe = [], '', 0, 0
    for c, a, b in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if c.isspace():
            if cur: out.append((t0 + cs, t0 + pe, cur)); cur = ''
            continue
        if not cur: cs = a
        cur += c; pe = b
    if cur: out.append((t0 + cs, t0 + pe, cur))
    return out

_lens = {}
def clip_len(f):
    if f not in _lens:
        out = subprocess.run([FF, '-i', str(P/f)], capture_output=True, text=True).stderr
        h, m, sec = out.split('Duration: ')[1].split(',')[0].split(':'); _lens[f] = int(h) * 3600 + int(m) * 60 + float(sec)
    return _lens[f]

def timeline():
    shots, audio, caps, events = [], [], [], []
    t = 0.0
    for sec in SCRIPT:
        if sec['type'] == 'vo':
            path = P/'assets'/'vo'/f'{sec["name"]}.wav'; meta = vo_meta(sec['name'])
            dur = len(wav_read(path)) / SR; pos = 0
            audio.append(('vo', t, path, 0, dur)); caps += vo_words(meta, t)
            for anchor, shot in PLAN.get(sec['name'], []):
                at, pos = anchor_time(meta, anchor, pos)
                shots.append(dict(shot, t=t + max(0, at - 0.05) if not (shots and abs(shots[-1]['t'] - t) < 0.01 and at < 0.3) else t, sec=sec['name'], kind='clip'))
            events.append(('vo', t, sec['name']))
            t += dur + 0.35
        elif sec['type'] == 'quote':
            a, b, _ = Q.resolve(sec); d = b - a
            src = hd(sec['clip'])
            shots.append(dict(kind='clip', file=src, start=a, t=t, sec=sec['name'], bw=sec['clip'] in OLD, tag=sec.get('card'), speaker=True))
            for off, cs in CUTAWAYS.get(sec['name'], []):
                if cs.get('keep_audio_time'): cs = dict(cs, start=a + off)
                shots.append(dict(cs, kind='clip', t=t + off, sec=sec['name']))
            audio.append(('quote', t, P/src, a, d))
            ws = Q.words(sec['clip']); raw = json.loads((P/'assets'/'clips'/f'{sec["clip"]}.words.json').read_text(encoding='utf-8'))
            for s in (raw if sec['clip'] not in NOCAP else []):
                for wa, wb, w in s['w']:
                    if a <= wa < b - 0.1: caps.append((t + wa - a, t + wb - a, w.strip()))
            events.append(('quote', t, sec['name']))
            t += d + 0.45
        elif sec['type'] == 'card':
            shots.append(dict(kind='card', file=TOUCH if 'etihad' in sec['name'] else SKYFA, start=46 if 'etihad' in sec['name'] else 106,
                              t=t, sec=sec['name'], lines=sec['lines'], credit=sec['credit']))
            events.append(('card', t, sec['name']))
            t += sec['dur'] + 0.3
        if sec['name'] == 'cold_open':
            shots.append(dict(kind='title', file=FAREWELL, start=366, t=t, sec='title')); events.append(('title', t, 'title')); t += 3.2
    t += 4.0  # end card
    shots.append(dict(kind='end', file=FAREWELL, start=574, t=t - 4.0, sec='end'))
    shots.sort(key=lambda s: s['t'])
    for x, y in zip(shots, shots[1:] + [dict(t=t)]):
        x['dur'] = round(y['t'] * FPS) / FPS - round(x['t'] * FPS) / FPS
        L = clip_len(x['file'])
        if x['start'] + x['dur'] > L - 0.3:
            x['start'] = max(0.0, round(L - x['dur'] - 0.4, 2))
    return [s for s in shots if s['dur'] > 0.05], audio, caps, events, t

def render_shot(i, sh):
    out = CL/f'shot_{i:03d}.mp4'
    frames = round((sh['t'] + sh['dur']) * FPS) - round(sh['t'] * FPS)
    key = json.dumps({k: v for k, v in sh.items() if k not in ('txt', 't', 'sec')}, sort_keys=True, default=str) + str(frames) + str(i if sh.get('txt') or sh['kind'] != 'clip' else '') + 'v2'
    digest = hashlib.sha256(key.encode()).hexdigest(); rec = out.with_suffix('.sha')
    if out.exists() and rec.exists() and rec.read_text() == digest: return out
    zoom = 0.0007 if sh.get('slow') else 0.0012
    if sh.get('speaker'): zoom = 0.0005
    grade = 'eq=contrast=1.12:saturation=0.45:brightness=-0.02:gamma=0.95'
    if sh.get('bw'): grade = 'hue=s=0,eq=contrast=1.2:brightness=-0.02'
    base = (f"scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,fps={FPS},"
            f"zoompan=z='1+{zoom}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},{grade},noise=alls=6:allf=t,vignette=PI/4.5")
    src = ['-ss', str(sh['start']), '-i', str(P/sh['file'])]
    overlay = None
    if sh['kind'] == 'card': overlay = G.quote_card(sh['lines'], sh['credit']); base += ',gblur=sigma=10,eq=brightness=-0.15'
    elif sh['kind'] == 'title': overlay = G.title('WENGER', 'KNEW')
    elif sh['kind'] == 'end': overlay = G.title('WOULD YOU HAVE', 'LISTENED?'); base += ',eq=brightness=-0.12'
    elif sh.get('txt'): overlay = sh['txt']; base += ',eq=brightness=-0.12'
    elif sh.get('tag'): overlay = G.date_tag(sh['tag'])
    if overlay:
        mov = CL/f'ov_{i:03d}.mov'; G.render(overlay, frames / FPS, mov)
        cmd = [FF, '-y', *src, '-i', str(mov), '-an', '-filter_complex', f"[0:v]{base}[bg];[1:v]format=rgba[fg];[bg][fg]overlay=0:0:format=auto,format=yuv420p[v]", '-map', '[v]', '-frames:v', str(frames)]
    else:
        cmd = [FF, '-y', *src, '-an', '-vf', base, '-frames:v', str(frames)]
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-video_track_timescale', '15360', str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: raise RuntimeError(f'shot {i}: ' + p.stderr[-1500:])
    rec.write_text(digest)
    for m in CL.glob(f'ov_{i:03d}.mov'): m.unlink()
    return out

def safe_render(i, sh):
    for k in range(3):
        try: return render_shot(i, sh)
        except RuntimeError as e:
            if k == 2: raise
            print('retry', i, flush=True)

MUSIC = [('Lightless Dawn', 0.0), ('Long Note Four', None), ('Heartbreaking', 'ending')]

def music_bed(total, events):
    """Three incompetech cues: tension for the open, ambient bed for the story, sad cue for the ending."""
    def load(name):
        w = P/'_tmp'/f'm_{name}.wav'
        if not w.exists(): subprocess.run([FF, '-y', '-i', str(P/'assets'/'music'/f'{name}.mp3'), '-ar', str(SR), '-ac', '2', str(w)], check=True, capture_output=True)
        return wav_read(w)
    n = int(total * SR) + SR; bed = np.zeros((n, 2), np.float32)
    title_t = [e[1] for e in events if e[0] == 'title'][0]
    end_t = [e[1] for e in events if e[2] == 'fair'][0]
    def place(name, s, e, gain, fi=1.0, fo=2.5, offset=0):
        a = load(name); a = a[int(offset * SR):]
        L = int((e - s) * SR)
        while len(a) < L: a = np.concatenate([a, a])
        a = a[:L].copy(); a[:int(fi * SR)] *= np.linspace(0, 1, int(fi * SR))[:, None]; a[-int(fo * SR):] *= np.linspace(1, 0, int(fo * SR))[:, None]
        bed[int(s * SR):int(s * SR) + L] += a * gain
    place('Lightless Dawn', 0, title_t + 3.0, 0.32, 0.5, 2.0)
    place('Long Note Four', title_t + 2.0, end_t + 3, 0.30, 3.0, 4.0, offset=10)
    place('Heartbreaking', end_t, total, 0.30, 3.0, 4.0)
    return bed

def mix(audio, events, total):
    n = int(total * SR) + SR; voice = np.zeros((n, 2), np.float32); quote_mask = np.zeros(n, np.float32)
    for kind, t, path, a, d in audio:
        if kind == 'vo': x = wav_read(path)
        else:
            tmp = P/'_tmp'/f'q_{hashlib.md5((str(path) + str(a)).encode()).hexdigest()[:8]}.wav'
            if not tmp.exists():
                subprocess.run([FF, '-y', '-ss', str(a), '-t', str(d), '-i', str(path), '-vn', '-af', f'highpass=f=80,loudnorm=I=-16:TP=-1.5,afade=t=in:d=0.06,afade=t=out:st={max(0, d - 0.2)}:d=0.2', '-ar', str(SR), '-ac', '2', str(tmp)], check=True, capture_output=True)
            x = wav_read(tmp); quote_mask[int(t * SR):int(t * SR) + len(x)] = 1
        s = int(t * SR); voice[s:s + len(x)] += x[:n - s]
    env = (np.abs(voice).max(axis=1) > 0.02).astype(np.float64)
    win = int(0.3 * SR); c = np.concatenate([[0], np.cumsum(env)]); h = win // 2; idx = np.arange(n)
    act = np.clip((c[np.minimum(idx + h, n)] - c[np.maximum(idx - h, 0)]) / win * 3, 0, 1)
    bed = music_bed(total, events)[:n] * (1 - 0.6 * act[:, None]) * (1 - 0.5 * quote_mask[:, None])
    sfx = np.zeros_like(voice)
    S_ = {k: wav_read(P/'assets'/'sfx'/f'{k}.wav') for k in ['whoosh', 'hit', 'riser']}
    def drop(k, t, g):
        a = S_[k]; s = max(0, int(t * SR)); sfx[s:s + len(a)] += a[:n - s] * g
    for e in events:
        if e[0] == 'card': drop('hit', e[1], 0.3)
        if e[0] == 'title': drop('riser', e[1] - 2.3, 0.3); drop('hit', e[1] + 0.1, 0.45)
    out = voice + bed + sfx
    out = np.tanh(out * 0.95) / np.tanh(0.95)
    wav_write(P/'_tmp'/'mix.wav', out[:int(total * SR)])
    subprocess.run([FF, '-y', '-i', str(P/'_tmp'/'mix.wav'), '-af', 'loudnorm=I=-14:TP=-1:LRA=9', '-ar', str(SR), str(P/'_tmp'/'mix_ln.wav')], check=True, capture_output=True)
    return P/'_tmp'/'mix_ln.wav'

def ass_time(x): return f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'
def write_captions(caps, path):
    words = sorted(caps); chunks, cur = [], []
    for k, (a, b, w) in enumerate(words):
        cur.append((a, b, w)); nxt = words[k + 1][0] if k + 1 < len(words) else None
        if len(cur) >= 4 or w[-1:] in '.?!,' or nxt is None or nxt - b > 0.45 or len(' '.join(x[2] for x in cur)) > 22:
            chunks.append(cur); cur = []
    lines = []
    for k, c in enumerate(chunks):
        a = c[0][0]; b = c[-1][1] + 0.25
        if k + 1 < len(chunks): b = min(b, chunks[k + 1][0][0])
        lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{' '.join(x[2] for x in c).upper()}")
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Cap,Anton,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,6,2,2,80,80,100,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    Path(path).write_text(head + '\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == '__main__':
    shots, audio, caps, events, total = timeline()
    print(f'{len(shots)} shots, runtime {total:.1f}s ({int(total // 60)}:{int(total % 60):02d})')
    if '--plan' in sys.argv:
        for s in shots: print(f"{s['t']:7.2f} {s['dur']:5.2f} {s['sec']:16} {s['kind']:5} {Path(s['file']).stem}@{s['start']:.1f}")
        sys.exit()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        paths = list(pool.map(lambda a: safe_render(*a), enumerate(shots)))
    cat = P/'_tmp'/'concat.txt'; cat.write_text('\n'.join(f"file '{p.as_posix()}'" for p in paths))
    video = P/'_tmp'/'video.mp4'
    subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', str(cat), '-c', 'copy', str(video)], check=True, capture_output=True)
    aud = mix(audio, events, total)
    capf = P/'captions.ass'; write_captions(caps, capf)
    esc = lambda p: p.as_posix().replace(':', '\\:')
    final = P/'final video'/'wenger-knew.mp4'
    p = subprocess.run([FF, '-y', '-i', str(video), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-vf', f"ass='{esc(capf)}':fontsdir='{esc(P/'assets'/'fonts')}'",
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', str(final)], capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-1500:])
    (P/'shot_timeline.json').write_text(json.dumps([{k: v for k, v in s.items() if k != 'txt'} for s in shots], indent=1, default=str), encoding='utf-8')
    print('Done', final)
