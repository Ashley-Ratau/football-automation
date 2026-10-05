"""Build 'Carrick's United is already falling apart' — quote-driven documentary.

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
BRI, CITY, FUL, HULL, IPS, LIV = br('brighton'), br('city'), br('fulham'), br('hull'), br('ipswich'), br('liverpool')
PRESSER, SKYNEWS, SKYQA = hd('Qiob0M7_kCI'), hd('UFmtSYY2C3k'), hd('c1_jF2ZwlfU')
FAREWELL = BRI  # title / end card background

def S(f, s, **o): return dict(file=f, start=s, **o)
K = G.kinetic

PLAN = {
 'cold_open': [
  ('Sixteenth of September', S(BRI, 12)),
  ('Twelve minutes in', S(BRI, 90, txt=K('2-0 UP', size=170, sub='12 minutes · Old Trafford'))),
  ('Then it all falls apart', S(BRI, 270, slow=True)),
  ('Brighton score three', S(BRI, 365)),
  ('United are out', S(BRI, 535)),
  ('for the first time in fifty', S(BRI, 600, txt=K('FIRST TIME IN 50 YEARS', size=110, color=G.RED))),
  ('Michael Carrick walks', S(PRESSER, 3)),
 ],
 'the_question': [
  ('Eight months ago', S(LIV, 32)),
  ('Now, after just five', S(BRI, 422, slow=True)),
  ('So how did', S(BRI, 588, bw=True)),
 ],
 'the_rescue': [
  ('Go back to January', S(SKYNEWS, 30)),
  ('Ruben Amorim', S(SKYNEWS, 33, bw=True, txt=K('JANUARY 2026', size=140, sub='Amorim sacked'))),
  ('United turn to', S(SKYQA, 20)),
  ('Not everyone', S(hd('q98dtA1EFnY'), 5)),
 ],
 'the_run': [
  ('What happened next', S(LIV, 18)),
  ('Seventeen league games', S(LIV, 45, txt=K('12W · 3D · 2L', size=150, sub='17 Premier League games as interim'))),
  ('Wins over City', S(LIV, 120)),
  ('Over that stretch', S(LIV, 280)),
  ('United finished third', S(LIV, 520, txt=K('3RD', size=200, sub='Champions League qualified'))),
 ],
 'the_deal': [
  ('So United gave', S(SKYNEWS, 110)),
  ('A two-year contract', S(SKYNEWS, 116, txt=K('CONTRACT TO 2028', size=130))),
  ('And here is where', S(LIV, 190, slow=True)),
  ('Because when you look', S(LIV, 300)),
  ('Carrick has said', S(PRESSER, 400)),
 ],
 'the_summer': [
  ('Then came the summer', S(SKYNEWS, 190)),
  ('Casemiro left', S(SKYNEWS, 194)),
  ('But for a club', S(SKYQA, 300)),
  ('The squad that started', S(HULL, 10)),
  ('Only now', S(CITY, 30)),
 ],
 'the_slide': [
  ('Opening day', S(HULL, 2)),
  ('United lose two-nil', S(HULL, 132, txt=K('HULL 2-0 UNITED', size=130))),
  ('A week later', S(IPS, 60)),
  ('and it looks like', S(IPS, 405)),
  ("It wasn't", S(IPS, 630, bw=True)),
  ('A two-all draw', S(CITY, 165, txt=K('EVERTON 2-2', size=140))),
  ('Then the derby', S(CITY, 2)),
  ('City go down', S(CITY, 60)),
  ('and United still lose', S(CITY, 375, txt=K('UNITED 0-1 CITY', size=130, sub='vs ten men'))),
  ('Three days later', S(BRI, 380)),
  ('And then a late', S(FUL, 18)),
 ],
 'the_numbers': [
  ('Here is the number', S(BRI, 600, bw=True)),
  ('In seventeen league', S(LIV, 60, bw=True, txt=K('INTERIM: 2 DEFEATS', size=120, sub='17 league games'))),
  ('This season, in all', S(BRI, 540, txt=K('THIS SEASON: 3 DEFEATS', size=110, color=G.RED, sub='already'))),
  ('One win in five', S(FUL, 420, txt=K('12TH', size=200, sub='1 win in 5 league games'))),
 ],
 'the_why': [
  ('So what has changed', S(SKYQA, 120)),
  ('Last season', S(LIV, 245)),
  ('They sat deep', S(LIV, 300)),
  ('This season, opponents', S(CITY, 225)),
  ('Teams drop off', S(FUL, 240)),
  ('Against Brighton', S(BRI, 485)),
  ('they did not have another', S(BRI, 545, txt=K("76'", size=200, sub='next shot on target after 2-0'))),
 ],
 'the_crowd': [
  ('And the crowd', S(BRI, 450)),
  ('At full time', S(BRI, 625, bw=True)),
  ('Carrick was asked', S(hd('un8y4WoorNk'), 190)),
 ],
 'the_spiral': [
  ('This is the part', S(BRI, 590, slow=True)),
  ('A manager arrives', S(LIV, 32)),
  ('He gets the job', S(SKYNEWS, 116)),
  ('And then the club', S(CITY, 375, bw=True)),
  ('Moyes, Van Gaal', S(CITY, 590, bw=True, txt=K('MOYES · VAN GAAL · MOURINHO', size=84, sub='SOLSKJAER · TEN HAG · AMORIM'))),
  ("Keane's real warning", S(hd('q98dtA1EFnY'), 40)),
 ],
 'fair': [
  ('Now, to be fair', S(IPS, 160)),
  ('United are still', S(IPS, 300, txt=K('4-0', size=200, sub='Champions League opener'))),
  ('Carrick has turned', S(LIV, 400)),
 ],
 'ending': [
  ('After the international', S(CITY, 600)),
  ('Win, and this', S(IPS, 180)),
  ('Lose, and the questions', S(BRI, 595, bw=True)),
  ('Eight months ago', S(LIV, 590)),
  ('Now he has to', S(BRI, 422, slow=True, bw=True)),
 ],
 'outro': [
  ('Is Carrick the right', S(BRI, 588, slow=True)),
 ],
}
# cutaways inside long soundbites: (offset seconds into the quote, shot)
CUTAWAYS = {
 'q_on_me': [(5.0, S(BRI, 625, bw=True))],
}
NOCAP = set()
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
            for s in (raw if sec['clip'] not in NOCAP else []):
                for wa, wb, w in s['w']:
                    if a <= wa < b - 0.1: caps.append((t + wa - a, t + wb - a, w.strip()))
            events.append(('quote', t, sec['name']))
            t += d + 0.45
        elif sec['type'] == 'card':
            shots.append(dict(kind='card', file=BRI, start=600,
                              t=t, sec=sec['name'], lines=sec['lines'], credit=sec['credit']))
            events.append(('card', t, sec['name']))
            t += sec['dur'] + 0.3
        if sec['name'] == 'cold_open':
            shots.append(dict(kind='title', file=FAREWELL, start=588, t=t, sec='title')); events.append(('title', t, 'title')); t += 3.2
    t += 4.0  # end card
    shots.append(dict(kind='end', file=FAREWELL, start=600, t=t - 4.0, sec='end'))
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
    elif sh['kind'] == 'title': overlay = G.title("CARRICK'S", 'COLLAPSE')
    elif sh['kind'] == 'end': overlay = G.title('TOO SOON', 'OR TOO LATE?'); base += ',eq=brightness=-0.12'
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
    final = P/'final video'/'carricks-united-is-falling-apart.mp4'
    p = subprocess.run([FF, '-y', '-i', str(video), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-vf', f"ass='{esc(capf)}':fontsdir='{esc(P/'assets'/'fonts')}'",
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', str(final)], capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-1500:])
    (P/'shot_timeline.json').write_text(json.dumps([{k: v for k, v in s.items() if k != 'txt'} for s in shots], indent=1, default=str), encoding='utf-8')
    print('Done', final)
