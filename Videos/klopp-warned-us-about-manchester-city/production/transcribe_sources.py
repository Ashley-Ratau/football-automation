from pathlib import Path
import json
from faster_whisper import WhisperModel

P=Path(__file__).resolve().parents[1]
model=WhisperModel('tiny.en',device='cpu',compute_type='int8',cpu_threads=2)
for name,offset in [('2022',265),('cas',0)]:
    target=P/'_tmp'/f'{name}_transcript.json'
    if target.exists(): continue
    segments,info=model.transcribe(str(P/'_tmp'/f'{name}_speech.wav'),language='en',word_timestamps=True,beam_size=1)
    result=[]
    for s in segments:
        entry={'start':round(s.start+offset,2),'end':round(s.end+offset,2),'text':s.text,'words':[{'start':round(w.start+offset,2),'end':round(w.end+offset,2),'text':w.word} for w in s.words or []]}
        result.append(entry)
        print(f"{name} {entry['start']:.2f}-{entry['end']:.2f} {s.text}",flush=True)
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
