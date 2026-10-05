from pathlib import Path
from faster_whisper import WhisperModel
P=Path(__file__).resolve().parents[1]
model=WhisperModel('tiny.en',device='cpu',compute_type='int8',cpu_threads=2)
segments,_=model.transcribe(str(P/'_tmp/all_vo_listen.mp3'),beam_size=1,language='en')
text='\n'.join(s.text for s in segments)
(P/'_tmp/vo_openings_transcript.txt').write_text(text,encoding='utf-8')
print(text)
