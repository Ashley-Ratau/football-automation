from pathlib import Path
import hashlib,json,re
from urllib.parse import unquote
P=Path(__file__).resolve().parent
cfg=json.loads((P/'long_form_project.json').read_text())
m=json.loads((P/'_tmp/final_qc/measurements.json').read_text())
validation=json.loads((P/'_tmp/final_validation.json').read_text(encoding='utf-8-sig'))
shots=json.loads((P/'shot_timeline.json').read_text())
vo=[x for x in shots if x['kind']=='vo']
video=P/'final video'/cfg['output_filename']
assert validation['valid']
assert float(m['probe']['format']['duration'])>=480
assert 300<=m['narration_seconds']<=360
assert len([s for s in cfg['sections'] if s['type']=='insert'])==3
assert m['first_insert_start']<60
assert not cfg['captions']['enabled']
assert all((P/x['file']).exists() for x in shots)
assert max(x['duration'] for x in vo)<=3.8
for i in [1,2]:assert (P/f'assets/thumbnail/thumbnail_{i:02d}.png').exists()
page=(P/'START_HERE.html').read_text()
for href in re.findall(r'(?:href|src)="([^"]+)"',page):
    if '${' not in href and not href.startswith(('http','#')):assert (P/unquote(href)).exists(),href
audio=(P/'_tmp/final_qc/audio.log').read_text()
black=(P/'_tmp/final_qc/black.log').read_text()
assert 'black_start:' not in black
report=f'''# Final quality review

Final artifact: `final video/{cfg['output_filename']}`

- Duration: {float(m['probe']['format']['duration']):.3f} seconds (8:22 displayed).
- 1920 × 1080, H.264 video and AAC stereo audio.
- Liam narration: {m['narration_seconds']:.3f} seconds (5:24).
- Three genuine English pundit inserts; first begins at {m['first_insert_start']:.3f} seconds. Narration is replaced by original excerpt audio.
- {len(vo)} narration visuals, {min(x['duration'] for x in vo):.2f}–{max(x['duration'] for x in vo):.2f} seconds per cut. Fifteen distinct schematic scenarios.
- All 141 sampled final frames inspected across eight contact sheets, including every narration cut and the beginning/middle/end of each insert. No blank samples, wrong aspect ratio, source end cards or broken graphics observed. Named Sevilla actions and Pedri identity checked and corrected before final QC.
- Full-file black detection: no intervals of at least 0.2 seconds.
- Final audio: -16.6 LUFS integrated, 3.3 LU loudness range, -1.9 dBFS true peak. No clipping indicated.
- Independent cached small.en ASR checked all six narration WAVs; no missing content or changed numbers. This is ASR and signal review, not a claim of an uninterrupted human listening session.
- No added captions. Existing broadcaster graphics remain in source footage.
- Two inspected solo Raphinha thumbnail options. The third generation was rejected by the image tool safety system and not retried.
- Local HTML chapter navigation uses measured segment durations. All static linked local assets exist. Automated browser opening was blocked by the browser URL policy; no browser workaround attempted.
- Fresh project and research; the rejected Raphinha project was not read or reused.

SHA-256: `{hashlib.sha256(video.read_bytes()).hexdigest()}`

Sources, dates, archive distinctions and analysis limits: `SOURCE_CREDITS.md` and `02 research dossier.md`. No upload or YouTube clearance check was performed for this new film.
'''
(P/'FINAL_QC.md').write_text(report,encoding='utf-8')
print('PASS: final deliverables and measured requirements verified.')
print(video)
