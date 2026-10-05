"""Cache a word-timed transcript of the finished Raphinha video's audio."""
import json
from pathlib import Path
from faster_whisper import WhisperModel

root = Path(__file__).resolve().parents[1]
edit = Path(__file__).resolve().parent
source = root / 'final video' / 'the-raphinha-experiment-will-break-la-liga.mp4'
target = edit / 'word_transcript.json'
if target.exists():
    print(f'Using cached {target}')
else:
    model = WhisperModel('small.en', device='cpu', compute_type='int8')
    segments, info = model.transcribe(str(source), beam_size=5, language='en',
                                      word_timestamps=True, vad_filter=True,
                                      condition_on_previous_text=False)
    result = []
    for i, segment in enumerate(segments):
        result.append({'start': segment.start, 'end': segment.end, 'text': segment.text,
                       'words': [{'start': w.start, 'end': w.end, 'word': w.word,
                                  'probability': w.probability} for w in (segment.words or [])]})
        if i % 10 == 0:
            print(f'{segment.end:.1f}s transcribed', flush=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved {len(result)} segments to {target}')
