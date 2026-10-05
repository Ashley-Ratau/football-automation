"""Short, single-line burned-caption cues from cached word timestamps."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
edit = Path(__file__).resolve().parent
segments = json.loads((edit / 'word_transcript.json').read_text(encoding='utf-8'))
insert1 = edit / 'insert1_words.json'
if insert1.exists():
    replacement = json.loads(insert1.read_text(encoding='utf-8'))
    start = 33.064714
    for s in replacement:
        if s['start'] >= 24.8:
            continue
        t = dict(s)
        t['start'] += start
        t['end'] += start
        t['words'] = [{**w, 'start': w['start'] + start, 'end': w['end'] + start}
                      for w in s['words'] if w['start'] < 24.8]
        segments.append(t)
segments.sort(key=lambda s: s['start'])

report = json.loads((root / 'final video' / 'build_report.json').read_text(encoding='utf-8'))
inserts = []
offset = 0.0
for section in report['timeline']:
    if section['type'] == 'insert':
        inserts.append((offset, offset + section['duration']))
    offset += section['duration']

words = []
for s in segments:
    for w in s['words']:
        if w['start'] is None or w['end'] is None:
            continue
        midpoint = (float(w['start']) + float(w['end'])) / 2
        if any(a <= midpoint < b for a, b in inserts):
            continue
        token = w['word'].strip()
        if not token:
            continue
        token = re.sub(r'(?i)\b(rafina|raffina|rafinha)\b', 'Raphinha', token)
        token = re.sub(r'(?i)\b(hizlop|hislup)\b', 'Hislop', token)
        token = re.sub(r'(?i)\b(lamineamal)\b', 'Lamine Yamal', token)
        token = re.sub(r'(?i)\b(aicano)\b', 'Vallecano', token)
        token = re.sub(r'(?i)\b(hercules)\b', 'Herculez', token)
        words.append({'start': max(0, float(w['start'])), 'end': float(w['end']), 'text': token})
words.sort(key=lambda w: w['start'])

cues = []
current = []
def flush():
    if not current:
        return
    text = ' '.join(w['text'] for w in current)
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    cues.append({'start': current[0]['start'], 'end': current[-1]['end'], 'text': text})
    current.clear()

for w in words:
    if current:
        trial = ' '.join(x['text'] for x in current + [w])
        if (w['start'] - current[-1]['end'] > .42 or len(current) >= 4 or
            len(trial) > 29 or w['end'] - current[0]['start'] > 2.0 or
            current[-1]['text'].endswith(('.', '?', '!'))):
            flush()
    current.append(w)
flush()

# Preserve quick final words instead of dropping sub-350ms orphan cues.
merged_cues = []
for cue in cues:
    if (cue['end'] - cue['start'] < .35 and merged_cues and
        cue['start'] - merged_cues[-1]['end'] < .18 and
        len(merged_cues[-1]['text'] + ' ' + cue['text']) <= 30 and
        len((merged_cues[-1]['text'] + ' ' + cue['text']).split()) <= 5):
        merged_cues[-1]['text'] += ' ' + cue['text']
        merged_cues[-1]['end'] = cue['end']
    else:
        merged_cues.append(cue)
cues = merged_cues

def ass_time(seconds):
    centis = max(0, round(seconds * 100))
    h, rem = divmod(centis, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'

header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Narration,Arial,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,1,2,100,100,66,1
Style: Insert,Arial,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,1,2,100,100,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
lines = [header]
for cue in cues:
    if any(a <= cue['start'] < b for a, b in inserts):
        continue
    for a, b in inserts:
        if cue['start'] < a < cue['end']:
            cue['end'] = a
    if cue['end'] - cue['start'] < .35:
        continue
    text = cue['text'].replace('\\', r'\\').replace('{', '(').replace('}', ')')
    end = cue['end']
    lines.append(f"Dialogue: 0,{ass_time(cue['start'])},{ass_time(end)},Narration,,0,0,0,,{text}\n")

target = edit / 'captions.ass'
target.write_text(''.join(lines), encoding='utf-8-sig')
(edit / 'captions_cues.json').write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(cues)} single-line cues; max words {max(len(c["text"].split()) for c in cues)}; {target}')
