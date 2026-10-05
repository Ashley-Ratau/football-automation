"""Build 'The Ballon d'Or Race Isn't Even Close'.

Narration is the timeline: every shot starts on a word of the ElevenLabs alignment.
Shots are either graded footage (slow push-in) or animated graphics composited
over blurred, darkened footage. Audio is mixed in numpy: normalized VO, three
original music cues with VO ducking, and sound-design hits.
"""
from pathlib import Path
import json, wave, subprocess, hashlib, concurrent.futures, sys
import numpy as np
import gfx as G

P = Path(__file__).resolve().parent
FF = G.FF
B = P/'assets'/'broll'
CL = P/'_tmp'/'clips'; CL.mkdir(parents=True, exist_ok=True)
FPS = 30; SR = 44100
SECTIONS = json.loads((P/'script_sections.json').read_text(encoding='utf-8'))

KANE36 = 'kane_36_goals.mp4'; POKAL = 'kane_pokal_final.mp4'; FINAL = 'wc_final.mp4'
TROPHY = 'wc_trophy.mp4'; SEMI = 'wc_semi_france.mp4'; QF = 'wc_qf_belgium.mp4'
QFSKILL = 'wc_qf_skill.mp4'; SAUDI = 'wc_saudi.mp4'; BEST = 'yamal_best_2526.mp4'
VILLA = 'barca_villarreal_hattrick.mp4'; PARADE = 'barca_parade.mp4'; MBAPPE = 'mbappe_golden_boot.mp4'

def C(f, s, **o): return dict(kind='clip', file=f, start=s, **o)
def X(g, f, s, sfx=None, **o): return dict(kind='gfx', g=g, file=f, start=s, sfx=sfx, **o)

W_, GOLD, KANE, RED = G.WHITE, G.GOLD, G.KANE, G.RED

# (anchor phrase, shot) per section. Anchor = first occurrence after previous anchor.
PLAN = {
 'cold_open': [
  ('Sixty-one', X(G.big_number(61, 'Goals', 'Harry Kane · 2025/26 season', accent=KANE), KANE36, 49, 'hit')),
  ('A league title', C(KANE36, 129)),
  ('A cup final', C(POKAL, 106)),
  ('The European', C(POKAL, 283)),
  ("That is Harry", C(KANE36, 54.5)),
  ('Now here', C(FINAL, 8.6)),
  ('One goal', X(G.big_number(1, 'Goal', 'Lamine Yamal · World Cup 2026', count=False), FINAL, 10.5, 'hit')),
  ('Zero assists', X(G.big_number(0, 'Assists', 'Lamine Yamal · World Cup 2026', count=False), QF, 10, 'hit')),
  ('Eight matches', X(G.big_number(8, 'Matches', 'Lamine Yamal · World Cup 2026', count=False), SAUDI, 16, 'hit')),
  ('And the bookmakers', X(G.odds_board(), KANE36, 95, 'whoosh')),
  ('I think', C(TROPHY, 322)),
  ('And honestly', C(TROPHY, 381.5, slow=True)),
 ],
 'title': [('', X(G.title_card(), TROPHY, 386, 'hit'))],
 'the_rules': [
  ('Start with', C(TROPHY, 14)),
  ('It is not the Golden', C(MBAPPE, 0.5)),
  ('It is not a spread', C(KANE36, 41)),
  ('France Football', X(G.criteria(), TROPHY, 464, 'whoosh')),
  ('A season is judged', C(BEST, 8)),
  ('to the World Cup', C(FINAL, 1)),
  ('So the question', C(BEST, 58)),
  ('Who was the best', C(FINAL, 82.5)),
  ('Ask that', C(TROPHY, 202)),
 ],
 'exhibit_a': [
  ('Exhibit A', X(G.exhibit('A', 'La Liga 2025/26'), VILLA, 14, 'stamp')),
  ('Sixteen', C(BEST, 108)),
  ('More assists', C(BEST, 298)),
  ('A share', C(BEST, 68)),
  ('His first senior', C(VILLA, 133.5)),
  ('in February', C(VILLA, 39.5)),
  ('And at the end', C(PARADE, 202)),
  ('and Lamine was named', C(PARADE, 92)),
  ('But the numbers', C(BEST, 138)),
  ('Because every week', C(BEST, 186)),
  ('How do we', C(BEST, 460)),
  ('Double him', C(VILLA, 55.5)),
  ('Sit off him', C(BEST, 386)),
  ('Press him', C(BEST, 706)),
  ('Kane finishes', C(KANE36, 139, bw=True)),
  ('Yamal decides', C(BEST, 422)),
 ],
 'the_gravity': [
  ("There's a word", C(BEST, 328)),
  ('Gravity.', C(BEST, 552)),
  ('pull defenders', C(QF, 9.5)),
  ('Lamine might', C(QF, 75.5)),
  ('Watch the full', X(G.gravity(), QF, 46, 'whoosh')),
  ('That is where', C(VILLA, 103.5)),
  ("It doesn't show", C(BEST, 262)),
  ('It shows up in every', C(BEST, 488)),
 ],
 'exhibit_b': [
  ('Exhibit B', X(G.exhibit('B', 'The World Cup'), TROPHY, 32, 'stamp')),
  ("And yes", C(SAUDI, 16)),
  ('One goal, against', C(SAUDI, 28)),
  ('Arabia', C(SAUDI, 33.5)),
  ('Then four straight', C(QF, 50, bw=True)),
  ('People were asking', C(SEMI, 25.5, bw=True)),
  ('But watch the quarter', C(QF, 13)),
  ('No goal. No assist', C(QFSKILL, 0)),
  ('And he was still', C(QF, 112)),
  ('Because Belgium', C(QF, 45.5)),
  ('shifting their', C(QF, 40)),
  ('and Spain played', C(QF, 56)),
  ('Then France', C(SEMI, 112)),
  ('Then the final', C(FINAL, 9)),
  ('Spain one', C(FINAL, 60.5)),
  ('Argentina managed', C(FINAL, 43)),
  ('Spain did not', C(TROPHY, 182)),
  ('They won it', C(TROPHY, 382)),
 ],
 'the_kane_case': [
  ('Now, Harry', C(KANE36, 129)),
  ('Thirty-six', C(KANE36, 5)),
  ('Fourteen', C(KANE36, 25)),
  ('A hat-trick', C(POKAL, 106)),
  ('That is an out', C(POKAL, 278)),
  ('But look at', C(KANE36, 175, bw=True)),
  ('Bayern went', C(KANE36, 95, bw=True)),
  ('England led', C(POKAL, 70, bw=True)),
  ('In the two games', X(G.versus('Kane', 'Yamal', [('League goals', '36', '16', 'l'), ('League title', 'YES', 'YES', None), ('World Cup', 'SEMI-FINAL', 'WINNER', 'r')]), TROPHY, 464, 'whoosh')),
  ('And he won it', C(TROPHY, 386)),
 ],
 'the_others': [
  ('What about', C(MBAPPE, 1)),
  ('Kylian', C(MBAPPE, 13)),
  ('Brilliant', C(MBAPPE, 27)),
  ('But Real Madrid', C(MBAPPE, 39, bw=True)),
  ('and France went', C(SEMI, 104, bw=True)),
  ('And Ousmane', C(SEMI, 2)),
  ('PSG won', C(SEMI, 30)),
  ('Nobody else', X(G.trophy_cabinet(), TROPHY, 464, 'whoosh')),
 ],
 'the_verdict': [
  ('So here is', C(TROPHY, 538)),
  ('Kane had', C(KANE36, 89, bw=True)),
  ('Mbappé had', C(MBAPPE, 3, bw=True)),
  ('But Lamine', C(BEST, 242)),
  ('and an undroppable', C(FINAL, 11)),
  ('And he did all', C(TROPHY, 202)),
  ('He is nineteen', X(G.big_number(19, 'Years old', "Youngest Ballon d'Or winner in history if he wins", count=False, color=GOLD), TROPHY, 322, 'hit')),
  ('The votes', C(TROPHY, 548)),
  ('On the twenty', C(TROPHY, 556)),
  ('we find out', C(TROPHY, 202.5)),
  ('Because if they', C(TROPHY, 382)),
  ("isn't even", C(TROPHY, 386)),
  ('Tell me', X(G.end_card(), TROPHY, 470)),
 ],
}

# Pundit inserts (own audio), placed after a section. start/end are seconds within the downloaded segment.
INSERTS = {
 'exhibit_b': dict(file='assets/pundits/burley.mp4', vtt='assets/pundits/dEieA1Zqr8k.en-orig.vtt', offset=415.0,
                   start=20.45, end=28.75, name='STEWART ROBSON', role='Former Arsenal midfielder · ESPN FC'),
 'the_others': dict(file='assets/pundits/golazo.mp4', vtt='assets/pundits/PDCIotsF4Lw.en-orig.vtt', offset=478.0,
                    start=27.9, end=45.3, name='CBS SPORTS GOLAZO', role="Who should win the Ballon d'Or?"),
}
PAUSES = {'the_verdict': ('Tell me', 1.3)}

def wav_read(path):
    with wave.open(str(path)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels())

def norm_vo(i, s):
    raw = P/'assets'/'vo'/f'{i:02d}_{s["name"]}_raw.wav'; out = raw.with_name(raw.stem.replace('_raw', '_norm') + '.wav')
    if not out.exists():
        subprocess.run([FF, '-y', '-i', str(raw), '-af', 'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=7', '-ar', str(SR), '-ac', '2', str(out)], check=True, capture_output=True)
    return out

caps, inserts = [], []

def wav_write(path, a):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())

def vo_words(meta, t0):
    al = meta['alignment']; ch = al['characters']; st = al['character_start_times_seconds']; en = al['character_end_times_seconds']
    out, cur, cs, pe = [], '', 0, 0
    for c, a, b in zip(ch, st, en):
        if c.isspace():
            if cur: out.append((t0 + cs, t0 + pe, cur)); cur = ''
            continue
        if not cur: cs = a
        cur += c; pe = b
    if cur: out.append((t0 + cs, t0 + pe, cur))
    return out

def vtt_words(ins, t0):
    import re
    txt = (P/ins['vtt']).read_text(encoding='utf-8'); ws = []
    for blk in txt.split('\n\n'):
        m = re.search(r'(\d\d):(\d\d):(\d\d\.\d+) -->', blk)
        if not m or '<c>' not in blk: continue
        line = [l for l in blk.split('\n') if '<c>' in l][0]
        ws.append((int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]), re.match(r'([^<]+)', line)[1].strip()))
        for tm, w in re.findall(r'<(\d\d:\d\d:\d\d\.\d+)><c>([^<]+)</c>', line):
            h, mi, sec = tm.split(':'); ws.append((int(h) * 3600 + int(mi) * 60 + float(sec), w.strip()))
    a, b = ins['offset'] + ins['start'], ins['offset'] + ins['end']
    sel = [(x, w.replace('&gt;&gt;', '').strip()) for x, w in ws if a - 0.05 <= x <= b - 0.3]
    sel = [(x, w) for x, w in sel if w]
    return [(t0 + x - a, t0 + (sel[k + 1][0] if k + 1 < len(sel) else b) - a, w) for k, (x, w) in enumerate(sel)]

def ass_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); sec = x % 60
    return f'{h}:{m:02d}:{sec:05.2f}'

def write_captions(path):
    words = sorted(caps); chunks = []; cur = []
    for k, (a, b, w) in enumerate(words):
        cur.append((a, b, w))
        nxt = words[k + 1][0] if k + 1 < len(words) else None
        if len(cur) >= 4 or w[-1] in '.?!,' or nxt is None or nxt - b > 0.45 or len(' '.join(x[2] for x in cur)) > 22:
            chunks.append(cur); cur = []
    lines = []
    for k, c in enumerate(chunks):
        a = c[0][0]; b = c[-1][1] + 0.25
        if k + 1 < len(chunks): b = min(b, chunks[k + 1][0][0])
        text = ' '.join(x[2] for x in c).upper().replace('{', '').replace('}', '')
        sty = 'CapHi' if any(t0 <= a < t0 + ins['end'] - ins['start'] + 0.3 for t0, ins in inserts) else 'Cap'
        lines.append(f'Dialogue: 0,{ass_time(a)},{ass_time(b)},{sty},,0,0,0,,{text}')
    head = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Cap,Anton,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,6,2,2,80,80,100,1\n"
        "Style: CapHi,Anton,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,6,2,2,80,80,300,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    Path(path).write_text(head + '\n'.join(lines) + '\n', encoding='utf-8')

def word_time(sec_json, text, anchor, after):
    al = sec_json['alignment']; chars = ''.join(al['characters'])
    k = chars.find(anchor, after)
    if k < 0: raise KeyError(f'anchor {anchor!r} not found')
    return al['character_start_times_seconds'][k], k + 1

def timeline():
    shots, vo, events = [], [], []
    caps.clear(); inserts.clear()
    t = 0.25
    for i, s in enumerate(SECTIONS, 1):
        meta = json.loads((P/'assets'/'vo'/f'{i:02d}_{s["name"]}_raw.json').read_text(encoding='utf-8'))
        path = norm_vo(i, s)
        if s['name'] in PAUSES:
            anchor, gap = PAUSES[s['name']]
            pt, _ = word_time(meta, s['text'], anchor, 0); pt -= 0.05
            a = wav_read(path); cut = int(pt * SR)
            a = np.concatenate([a[:cut], np.zeros((int(gap * SR), 2), np.float32), a[cut:]])
            path = P/'_tmp'/f'{s["name"]}_paused.wav'; wav_write(path, a)
            al = meta['alignment']
            al['character_start_times_seconds'] = [x + gap if x >= pt else x for x in al['character_start_times_seconds']]
            al['character_end_times_seconds'] = [x + gap if x >= pt else x for x in al['character_end_times_seconds']]
        dur = len(wav_read(path)) / SR
        caps.extend(vo_words(meta, t))
        vo.append((t, path, s['name']))
        pos = 0
        for anchor, shot in PLAN[s['name']]:
            wt, pos = word_time(meta, s['text'], anchor, pos)
            shots.append(dict(shot, t=t + max(0, wt - 0.06) if shots else 0, sec=s['name']))
        events.append(('section', t, s['name']))
        t += dur
        if s['name'] in ('the_gravity', 'the_kane_case'): t += 0.5
        if s['name'] == 'cold_open':
            t += 0.5
            shots.append(dict(PLAN['title'][0][1], t=t, sec='title')); events.append(('title', t, 'title'))
            t += 3.4
        elif s['name'] == 'the_verdict':
            t += 5.5
        else:
            t += 0.7
        if s['name'] in INSERTS:
            ins = INSERTS[s['name']]; d = ins['end'] - ins['start']
            shots.append(dict(kind='insert', file=ins['file'], start=ins['start'], name=ins['name'], role=ins['role'], t=t, sec='insert'))
            inserts.append((t, ins)); caps.extend(vtt_words(ins, t))
            events.append(('insert', t, s['name']))
            t += d + 0.6
    for a, b in zip(shots, shots[1:] + [dict(t=t)]):
        a['dur'] = round(b['t'] * FPS) / FPS - round(a['t'] * FPS) / FPS
    # cold open first shot starts at 0
    return shots, vo, events, t

def render_shot(i, sh):
    out = CL/f'shot_{i:03d}.mp4'
    frames = round((sh['t'] + sh['dur']) * FPS) - round(sh['t'] * FPS)
    key = json.dumps({k: v for k, v in sh.items() if k not in ('g', 't', 'sec')}, sort_keys=True) + str(frames) + ('' if sh['kind'] == 'clip' else str(i) + 'v3')
    digest = hashlib.sha256(key.encode()).hexdigest()
    rec = out.with_suffix('.sha')
    if out.exists() and rec.exists() and rec.read_text() == digest: return out
    zoom = 0.0009 if sh.get('slow') else 0.0016
    grade = 'eq=contrast=1.07:saturation=1.12:gamma=0.98'
    if sh.get('bw'): grade = 'hue=s=0,eq=contrast=1.18:brightness=-0.03'
    base = (f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps={FPS},"
            f"zoompan=z='1+{zoom}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},{grade},vignette=PI/5")
    src = ['-ss', str(sh['start']), '-i', str(B/sh['file'])]
    if sh['kind'] == 'insert':
        lt = CL/f'lt_{i:03d}.png'; G.lower_third(sh['name'], sh['role']).save(lt)
        fc = (f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps={FPS},eq=contrast=1.04:saturation=1.05[b];"
              f"[1:v]format=rgba,fade=t=in:st=0.3:d=0.4:alpha=1[l];[b][l]overlay=0:0:format=auto,format=yuv420p[v]")
        cmd = [FF, '-y', '-ss', str(sh['start']), '-i', str(P/sh['file']), '-loop', '1', '-i', str(lt), '-an', '-filter_complex', fc, '-map', '[v]', '-frames:v', str(frames)]
    elif sh['kind'] == 'clip':
        cmd = [FF, '-y', *src, '-an', '-vf', base, '-frames:v', str(frames)]
    else:
        mov = CL/f'gfx_{i:03d}.mov'
        G.render(sh['g'], frames / FPS, mov)
        fc = (f"[0:v]{base},gblur=sigma=14,eq=brightness=-0.10[bg];[1:v]format=rgba[fg];[bg][fg]overlay=0:0:format=auto,format=yuv420p[v]")
        cmd = [FF, '-y', *src, '-i', str(mov), '-an', '-filter_complex', fc, '-map', '[v]', '-frames:v', str(frames)]
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-video_track_timescale', '15360', str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-2000:])
    rec.write_text(digest)
    return out

def mix(shots, vo, events, total):
    n = int(total * SR) + SR
    voice = np.zeros((n, 2), np.float32)
    for t, path, _ in vo:
        a = wav_read(path); s = int(t * SR); voice[s:s + len(a)] += a
    for t, ins in inserts:
        tmpw = P/'_tmp'/(Path(ins['file']).stem + '_ins.wav')
        d = ins['end'] - ins['start']
        subprocess.run([FF, '-y', '-ss', str(ins['start']), '-t', str(d), '-i', str(P/ins['file']), '-vn', '-af',
                        f'loudnorm=I=-16:TP=-1.5,afade=t=in:d=0.08,afade=t=out:st={d - 0.25}:d=0.25', '-ar', str(SR), '-ac', '2', str(tmpw)], check=True, capture_output=True)
        a = wav_read(tmpw); st = int(t * SR); voice[st:st + len(a)] += a[:len(voice) - st]
    # VO activity envelope for ducking
    env = np.abs(voice).max(axis=1)
    win = int(0.25 * SR); k = np.ones(win) / win
    x = (env > 0.02).astype(np.float64); c = np.concatenate([[0], np.cumsum(x)]); h = win // 2
    idx = np.arange(len(x)); act = (c[np.minimum(idx + h, len(x))] - c[np.maximum(idx - h, 0)]) / win
    act = np.clip(act * 3, 0, 1)
    duck = 1.0 - 0.65 * act
    music = np.zeros_like(voice)
    def place(name, start, end, gain, fade_in=0.4, fade_out=1.5, loop_from=None):
        a = wav_read(P/'assets'/f'{name}.wav'); s = int(start * SR); L = int(end * SR) - s
        if len(a) < L and loop_from is not None:
            xf = int(2 * SR); body = a
            while len(body) < L:
                seg = a[int(loop_from * SR):]
                ramp = np.linspace(0, 1, xf)[:, None]
                body = np.concatenate([body[:-xf], body[-xf:] * (1 - ramp) + seg[:xf] * ramp, seg[xf:]])
            a = body
        a = a[:L].copy(); m = len(a)
        fi = int(fade_in * SR); fo = int(fade_out * SR)
        a[:fi] *= np.linspace(0, 1, fi)[:, None]; a[m - fo:] *= np.linspace(1, 0, fo)[:, None]
        music[s:s + m] += a * gain
    title_t = [e[1] for e in events if e[0] == 'title'][0]
    rules_t = [e[1] for e in events if e[2] == 'the_rules'][0]
    verdict_t = [e[1] for e in events if e[2] == 'the_verdict'][0]
    place('music_tension', 0, title_t + 0.25, 0.22, 0.05, 0.25)
    place('music_case', title_t + 0.2, verdict_t + 0.8, 0.15, 0.05, 1.6, loop_from=20)
    place('music_verdict', verdict_t - 0.6, total, 0.19, 1.2, 3.0)
    music *= duck[:, None]
    sfx = np.zeros_like(voice)
    S = {k: wav_read(P/'assets'/'sfx'/f'{k}.wav') for k in ['hit', 'whoosh', 'riser', 'stamp']}
    gains = {'hit': 0.55, 'whoosh': 0.4, 'stamp': 0.6, 'riser': 0.45}
    def drop(name, t):
        a = S[name]; s = max(0, int(t * SR)); sfx[s:s + len(a)] += a[:len(sfx) - s] * gains[name]
    for sh in shots:
        if sh.get('sfx'): drop(sh['sfx'], sh['t'] - (0.12 if sh['sfx'] == 'whoosh' else 0))
    drop('riser', title_t - 2.4)
    for e in events:
        if e[0] == 'insert': drop('whoosh', e[1] - 0.3)
        if e[0] == 'section' and e[2] not in ('cold_open', 'exhibit_a', 'exhibit_b', 'the_verdict'): drop('whoosh', e[1] - 0.35)
    out = voice + music + sfx
    out = np.tanh(out * 0.95) / np.tanh(0.95)
    out = out[:int(total * SR)]
    path = P/'_tmp'/'mix.wav'
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    final = P/'_tmp'/'mix_ln.wav'
    subprocess.run([FF, '-y', '-i', str(path), '-af', 'loudnorm=I=-14:TP=-1:LRA=9', '-ar', str(SR), str(final)], check=True, capture_output=True)
    return final

if __name__ == '__main__':
    shots, vo, events, total = timeline()
    print(f'{len(shots)} shots, runtime {total:.1f}s')
    if '--plan' in sys.argv:
        for s in shots: print(f"{s['t']:7.2f} {s['dur']:5.2f} {s['sec']:14} {s['kind']:4} {s['file']}@{s['start']}")
        write_captions(P/'captions.ass')
        sys.exit()
    bad = [s for s in shots if s['dur'] < 0.5]
    if bad: print('WARNING short shots', [(round(s['t'], 2), s['dur']) for s in bad])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        paths = list(pool.map(lambda a: render_shot(*a), enumerate(shots)))
    cat = P/'_tmp'/'concat.txt'; cat.write_text('\n'.join(f"file '{p.as_posix()}'" for p in paths))
    video = P/'_tmp'/'video.mp4'
    subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', str(cat), '-c', 'copy', str(video)], check=True, capture_output=True)
    audio = mix(shots, vo, events, total)
    final = P/'final video'/'the-ballon-dor-race-isnt-even-close.mp4'
    capf = P/'captions.ass'; write_captions(capf)
    esc = lambda p: p.as_posix().replace(':', '\\:')
    vf = f"ass='{esc(capf)}':fontsdir='{esc(P/'assets'/'fonts')}'"
    p = subprocess.run([FF, '-y', '-i', str(video), '-i', str(audio), '-map', '0:v', '-map', '1:a', '-vf', vf, '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', str(final)], capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-2000:])
    (P/'shot_timeline.json').write_text(json.dumps([{k: v for k, v in s.items() if k != 'g'} for s in shots], indent=1, ensure_ascii=False), encoding='utf-8')
    print('Done', final)
