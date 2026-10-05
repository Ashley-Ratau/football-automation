from pathlib import Path
from faster_whisper import WhisperModel
P=Path(__file__).resolve().parents[1]
m=WhisperModel('tiny.en',device='cpu',compute_type='int8',cpu_threads=2)
out=[]
for name in ['warning','cas','ceiling']:
    segments,_=m.transcribe(str(P/'assets/inserts'/f'{name}.mp4'),language='en',beam_size=1)
    text=' '.join(s.text for s in segments)
    out.append(f'{name}: {text}');print(out[-1],flush=True)
(P/'_tmp/insert_speech_check.txt').write_text('\n'.join(out),encoding='utf-8')
