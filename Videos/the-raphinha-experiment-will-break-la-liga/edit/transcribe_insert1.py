import json
from pathlib import Path
from faster_whisper import WhisperModel

root = Path(__file__).resolve().parents[1]
source = root / 'assets' / 'inserts' / 'insert_1.mp4'
target = root / 'edit' / 'insert1_words.json'
model = WhisperModel('small.en', device='cpu', compute_type='int8')
segments, _ = model.transcribe(str(source), beam_size=5, language='en',
                               word_timestamps=True, vad_filter=False,
                               condition_on_previous_text=False)
result = []
for s in segments:
    result.append({'start': s.start, 'end': s.end, 'text': s.text,
                   'words': [{'start': w.start, 'end': w.end, 'word': w.word,
                              'probability': w.probability} for w in (s.words or [])]})
    print(f'{s.start:.1f}-{s.end:.1f} {s.text}', flush=True)
target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
