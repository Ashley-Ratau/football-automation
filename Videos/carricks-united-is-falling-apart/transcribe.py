import sys, json
from pathlib import Path
from faster_whisper import WhisperModel
m = WhisperModel('small.en', compute_type='int8', cpu_threads=4)
for f in sys.argv[1:]:
    out = Path(f).with_suffix('.words.json')
    if out.exists(): continue
    segs, _ = m.transcribe(f, word_timestamps=True, vad_filter=True, condition_on_previous_text=False)
    data = [dict(s=s.start, e=s.end, t=s.text.strip(), w=[(w.start, w.end, w.word.strip()) for w in s.words]) for s in segs]
    out.write_text(json.dumps(data), encoding='utf-8')
    Path(f).with_suffix('.txt').write_text('\n'.join(f"{d['s']:7.1f} {d['t']}" for d in data), encoding='utf-8')
    print('done', f, flush=True)
