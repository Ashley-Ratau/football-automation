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

def hd(i): return f'assets/clips/{i}.mp4'
def br(n): return f'assets/broll/{n}.mp4'
def wb(n): return f'../wenger-warned-us/assets/broll/{n}.mp4'
FAREWELL, TR19, FF22, CT19 = br('klopp_farewell'), br('pl_title_race_2019'), br('pl_final_five_2022'), br('city_trophy_2019')
SKYFA, ITV, APPEAL = wb('sky_fa_statement_2026'), wb('itv_uefa_ban_2020'), wb('sky_city_appeal')
OCT22, BVB, ARRIVE = hd('62zh2Vb5AZg'), hd('Qpv0QXZmq5A'), hd('JozNmcK3Jhg')
CARD_BG = (SKYFA, 106)
TITLE = ('KLOPP', 'WAS RIGHT'); ENDCARD = ('WAS HE', 'RIGHT?'); TITLE_BG = (FAREWELL, 285); END_BG = (FAREWELL, 291)
OUTFILE = 'klopp-was-right.mp4'

def S(f, s, **o): return dict(file=f, start=s, **o)
K = G.kinetic

PLAN = {
 'cold_open': [
  ('On the twenty-ninth', S(SKYFA, 43)),
  ('an independent commission', S(SKYFA, 103)),
  ('sham sponsorship', S(SKYFA, 130)),
  ('more than nine hundred', S(SKYFA, 118, txt=K('£900,000,000+', size=150))),
  ('But there was another', S(SKYFA, 3)),
  ('From December twenty', S(SKYFA, 122, txt=K('DEC 2018 — FEB 2023', size=130))),
  ('concerted efforts', S(SKYFA, 146)),
  ('December twenty eighteen. Liverpool', S(TR19, 543)),
  ('Liverpool were top', S(TR19, 555)),
  ('And for the next four', S(hd('GbiW9GM9Wgg'), 8, bw=True)),
  ('kept telling us', S(FAREWELL, 63, slow=True)),
 ],
 'dortmund': [
  ('Jürgen Klopp built', S(BVB, 9)),
  ('At Borussia Dortmund', S(BVB, 25)),
  ('he won two league', S(BVB, 41)),
  ('a club that could', S(BVB, 57)),
  ('When he arrived', S(ARRIVE, 9)),
  ('Build a team', S(ARRIVE, 33)),
  ('Develop players', S(FAREWELL, 165)),
  ('Spend what you earn', S(FAREWELL, 147)),
  ('By twenty eighteen', S(TR19, 255)),
  ('Liverpool reached', S(TR19, 609)),
  ('only one team', S(TR19, 141)),
 ],
 'ninety_seven': [
  ('The twenty eighteen', S(TR19, 1131)),
  ('Liverpool lost one game', S(TR19, 1323)),
  ('They finished with', S(TR19, 1335, txt=K('LIVERPOOL: 97 POINTS', size=120))),
  ('City finished with', S(TR19, 1401, txt=K('CITY: 98', size=150, color=G.RED))),
 ],
 'pep_2019': [
  ('Three months later', S(TR19, 963)),
  ('Pep Guardiola was asked', S(hd('oxFG8jM4Bug'), 10)),
 ],
 'pep_2019_b': [
  ('When something is wrong', S(hd('oxFG8jM4Bug'), 252, bw=True, slow=True)),
  ('Remember that line', S(SKYFA, 126, slow=True)),
 ],
 'ban': [
  ('Liverpool won the league', S(FAREWELL, 207)),
  ('by eighteen points', S(FAREWELL, 213)),
  ('But in February', S(ITV, 18)),
  ('UEFA banned', S(ITV, 23)),
  ('for breaking', S(ITV, 26)),
  ("Klopp's first reaction", S(hd('AFxTfoxe410'), 0)),
 ],
 'cas': [
  ('Five months later', S(ITV, 42)),
  ('the Court of Arbitration', S(ITV, 46, txt=K('BAN OVERTURNED', size=150))),
  ('Some allegations', S(ITV, 62)),
  ('Klopp was asked', S(hd('F6mP5r32HK8'), 2)),
 ],
 'surprised': [
  ('Where you get the money', S(SKYFA, 146, bw=True)),
  ('A year later', S(SKYFA, 150)),
  ('Klopp was asked', S(hd('jPAPgMJH36c'), 2)),
 ],
 'ninety_two': [
  ('Twenty twenty-two', S(FF22, 1155)),
  ('Another title race', S(FF22, 1185)),
  ('Liverpool ninety-two', S(FF22, 1203, txt=K('LIVERPOOL: 92', size=150))),
  ('City ninety-three', S(FF22, 1263, txt=K('CITY: 93', size=150, color=G.RED))),
  ('One point. Again', S(FF22, 81, slow=True)),
 ],
 'haaland': [
  ('That summer', S(FF22, 651)),
  ('City signed Erling', S(OCT22, 30)),
  ('In October', S(OCT22, 60)),
  ('This is the press', S(OCT22, 290)),
 ],
 'legal': [
  ('Notice what he said', S(OCT22, 338, bw=True)),
  ("It's legal", S(OCT22, 344, bw=True, txt=K('“IT\'S LEGAL AND EVERYTHING IS FINE”', size=96))),
  ('Klopp never accused', S(FAREWELL, 231)),
  ('He just kept saying', S(FAREWELL, 243)),
  ('Four months later', S(SKYFA, 114)),
  ('charged City', S(SKYFA, 119, txt=K('115 CHARGES', size=160))),
  ('Pep Guardiola came out', S(hd('4F7psFr__rk'), 5)),
 ],
 'silent': [
  ('And Klopp', S(hd('vht4LI9yXw'), 17)),
  ('When the charges landed', S(hd('vht4LI9yXw'), 20)),
  ('This was his answer', S(hd('vht4LI9yXw'), 25)),
 ],
 'beer': [
  ('Klopp left Liverpool', S(FAREWELL, 21, slow=True)),
  ('In January twenty', S(hd('rxxnEI9zKh8'), 10)),
  ('he was asked', S(hd('rxxnEI9zKh8'), 60)),
 ],
 'verdict': [
  ('On the twenty-ninth', S(SKYFA, 43)),
  ('Guilty on almost', S(SKYFA, 3)),
  ('Sham contracts', S(SKYFA, 127)),
  ('More than nine hundred', S(SKYFA, 146)),
  ('And three of the four', S(SKYFA, 122)),
  ('By then, Klopp was', S(hd('96tsDiDPot0'), 2, cropsubs=True)),
  ('He was asked about it', S(hd('96tsDiDPot0'), 12, cropsubs=True)),
 ],
 'fair': [
  ('And to be fair', S(APPEAL, 34)),
  ("before Klopp's two", S(TR19, 1131, bw=True)),
  ('City deny', S(APPEAL, 46)),
  ('The punishment', S(APPEAL, 8)),
  ('Klopp does not want', S(FAREWELL, 75, slow=True)),
  ('He never asked', S(FAREWELL, 93)),
 ],
 'ending': [
  ('What he did, for years', S(OCT22, 320, bw=True)),
  ('Out loud', S(hd('AFxTfoxe410'), 10, bw=True)),
  ("City's money was different", S(hd('jPAPgMJH36c'), 45, bw=True)),
  ('The competition was not', S(hd('uh9mCg8qPKg'), 15, bw=True)),
  ('Someone should check', S(hd('F6mP5r32HK8'), 100, bw=True)),
  ('He was told it was', S(FAREWELL, 237)),
  ('That he was bitter', S(FAREWELL, 243)),
  ('That Liverpool should', S(FAREWELL, 261)),
  ('Now, a commission', S(SKYFA, 106, slow=True)),
 ],
 'outro': [('Jürgen Klopp was right', S(FAREWELL, 285, slow=True))],
}
CUTAWAYS = {
 'q_open': [(9.0, S(TR19, 1401)), (14.0, S(OCT22, 290))],
 'q_97': [(5.0, S(TR19, 1413))],
 'q_feel_pep': [(5.0, S(ITV, 110))],
 'q_cas': [(5.0, S(ITV, 46))],
 'q_germany': [(6.0, S(BVB, 30))],
 'q_beer': [(6.0, S(FAREWELL, 207))],
}
NOCAP = {'96tsDiDPot0', 'uh9mCg8qPKg'}
OLD = set()

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
            fixmap = sec.get('fix', {})
            for s in (raw if (sec['clip'] not in NOCAP and not sec.get('nocap')) else []):
                for wa, wb, w in s['w']:
                    if a <= wa < b - 0.1:
                        ww = w.strip(); core = ww.strip('.,?!'); ww = ww.replace(core, fixmap.get(core, fixmap.get(core.lower(), core))) if core else ww
                        caps.append((t + wa - a, t + wb - a, ww))
            events.append(('quote', t, sec['name']))
            t += d + 0.45
        elif sec['type'] == 'card':
            shots.append(dict(kind='card', file=CARD_BG[0], start=CARD_BG[1],
                              t=t, sec=sec['name'], lines=sec['lines'], credit=sec['credit']))
            events.append(('card', t, sec['name']))
            t += sec['dur'] + 0.3
        if sec['name'] == 'cold_open':
            shots.append(dict(kind='title', file=TITLE_BG[0], start=TITLE_BG[1], t=t, sec='title')); events.append(('title', t, 'title')); t += 3.2
    t += 4.0  # end card
    shots.append(dict(kind='end', file=END_BG[0], start=END_BG[1], t=t - 4.0, sec='end'))
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
    pre = 'crop=iw*0.78:ih*0.78:iw*0.11:0,' if sh.get('cropsubs') else ''
    base = (f"{pre}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,fps={FPS},"
            f"zoompan=z='1+{zoom}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},{grade},noise=alls=6:allf=t,vignette=PI/4.5")
    src = ['-ss', str(sh['start']), '-i', str(P/sh['file'])]
    overlay = None
    if sh['kind'] == 'card': overlay = G.quote_card(sh['lines'], sh['credit']); base += ',gblur=sigma=10,eq=brightness=-0.15'
    elif sh['kind'] == 'title': overlay = G.title(*TITLE)
    elif sh['kind'] == 'end': overlay = G.title(*ENDCARD); base += ',eq=brightness=-0.12'
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
        src = P/'assets'/'music'/f'{name}.mp3'
        if not w.exists() and not src.exists(): return None  # music is optional
        if not w.exists(): subprocess.run([FF, '-y', '-i', str(src), '-ar', str(SR), '-ac', '2', str(w)], check=True, capture_output=True)
        return wav_read(w)
    n = int(total * SR) + SR; bed = np.zeros((n, 2), np.float32)
    title_t = [e[1] for e in events if e[0] == 'title'][0]
    end_t = [e[1] for e in events if e[2] == 'fair'][0]
    def place(name, s, e, gain, fi=1.0, fo=2.5, offset=0):
        a = load(name)
        if a is None: return
        a = a[int(offset * SR):]
        L = int((e - s) * SR)
        while len(a) < L: a = np.concatenate([a, a])
        a = a[:L].copy(); a[:int(fi * SR)] *= np.linspace(0, 1, int(fi * SR))[:, None]; a[-int(fo * SR):] *= np.linspace(1, 0, int(fo * SR))[:, None]
        bed[int(s * SR):int(s * SR) + L] += a * gain
    place('Dark Times', 0, title_t + 3.0, 0.30, 0.5, 2.0)
    place('Echoes of Time v2', title_t + 2.0, end_t + 3, 0.28, 3.0, 4.0, offset=5)
    place('Lasting Hope', end_t, total, 0.30, 3.0, 4.0)
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
    final = P/'final video'/OUTFILE
    p = subprocess.run([FF, '-y', '-i', str(video), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-vf', f"ass='{esc(capf)}':fontsdir='{esc(P/'assets'/'fonts')}'",
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', str(final)], capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-1500:])
    (P/'shot_timeline.json').write_text(json.dumps([{k: v for k, v in s.items() if k != 'txt'} for s in shots], indent=1, default=str), encoding='utf-8')
    print('Done', final)
