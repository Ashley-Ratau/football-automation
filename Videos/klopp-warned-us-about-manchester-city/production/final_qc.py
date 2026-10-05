from pathlib import Path
import json,subprocess,re,concurrent.futures,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
SOURCE=P/'final video/klopp-warned-us-about-manchester-city.mp4'
OUT=Path(r'C:\Users\Wendy\Claude\Projects\Long Form Automation\klopp_man_city\YouTube Ready')
OUT.mkdir(parents=True,exist_ok=True)
FINAL=OUT/'Klopp Warned Us About Manchester City FINAL.mp4'
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-2400:])
    return r
def probe(f):return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(f)]).stdout)
# Constant-frame-rate hardware export removes timestamp irregularities at archive cuts.
run(['ffmpeg','-y','-loglevel','error','-threads','2','-i',str(SOURCE),'-map','0:v:0','-map','0:a:0','-vf','fps=30','-fps_mode','cfr','-c:v','h264_qsv','-global_quality','19','-preset','medium','-af','loudnorm=I=-16:TP=-1.7:LRA=9','-c:a','aac','-b:a','192k','-ar','44100','-ac','2','-movflags','+faststart',str(FINAL)])
spec=probe(FINAL); dur=float(spec['format']['duration']);video=next(s for s in spec['streams'] if s['codec_type']=='video');aud=next(s for s in spec['streams'] if s['codec_type']=='audio')
assert (video['width'],video['height'])==(1920,1080)
assert video['codec_name']=='h264' and aud['codec_name']=='aac'
assert video['avg_frame_rate']=='30/1'
assert 280<=dur<=600
assert abs(float(video.get('duration',dur))-float(aud.get('duration',dur)))<.3
Q=OUT/'QC';Q.mkdir(exist_ok=True)
cfg=json.loads((P/'long_form_project.json').read_text(encoding='utf-8-sig'))
report=json.loads((P/'final video/build_report.json').read_text(encoding='utf-8'))
frames=[]
times=[.6,3.6,11,25,42,68,95,120,150,185,220,255,285,320,dur-1]
times=[t for t in times if t<dur]
def frame(t):
    file=Q/f'frame_{t:06.1f}.jpg'
    run(['ffmpeg','-y','-loglevel','error','-threads','2','-ss',str(t),'-i',str(FINAL),'-frames:v','1','-vf','scale=480:270',str(file)])
    return t,file
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:frames=list(pool.map(frame,times))
canvas=Image.new('RGB',(1440,300*((len(frames)+2)//3)),(12,15,20));d=ImageDraw.Draw(canvas)
for i,(t,f) in enumerate(frames):canvas.paste(Image.open(f),(i%3*480,i//3*300));d.text((i%3*480+12,i//3*300+278),f'{t:.1f} seconds',fill='white')
canvas.save(Q/'contact_sheet.jpg',quality=92)
scan=run(['ffmpeg','-hide_banner','-threads','2','-i',str(FINAL),'-vf','blackdetect=d=0.3:pix_th=0.02','-af','silencedetect=noise=-45dB:d=1,ebur128=peak=true','-f','null','-'])
(Q/'decode_audio_scan.log').write_text(scan.stderr,encoding='utf-8')
silences=re.findall(r'silence_start: ([\d.]+)',scan.stderr)
black=re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',scan.stderr)
summary={'final_file':str(FINAL),'duration_seconds':dur,'resolution':[video['width'],video['height']],'fps':video['avg_frame_rate'],'video_codec':video['codec_name'],'audio_codec':aud['codec_name'],'music_bed':cfg['music_bed'],'sound_effects':len(cfg['sound_effects']),'inserts':sum(s['type']=='insert' for s in cfg['sections']),'decode_success':True,'black_intervals':black,'silence_starts':silences,'audio_summary':scan.stderr[scan.stderr.rfind('Summary:'):],'qc_method':'Visual sample inspection, complete decode, loudness/peak measurement, speech recognition of each narration opening. No full listening audition available.'}
if black:raise RuntimeError(f'Unexpected black interval: {black}')
if 'non monotonically increasing dts' in scan.stderr:raise RuntimeError('Final timestamp scan failed')
(Q/'qc_report.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
shutil.copy2(P/'assets/thumbnail/thumbnail_primary.png',OUT/'thumbnail.png')
for f in ['03 script.md','02 research dossier.md','04 clip map.csv','long_form_project.json']:
    shutil.copy2(P/f,OUT.parent/f)
(OUT.parent/'README.md').write_text(f'# Klopp video\n\nFinished export: YouTube Ready/{FINAL.name}\n\nFull editable source project: {P}\n\nVoice matched to Vinicius: ElevenLabs Liam, eleven_multilingual_v2, 1.15x. No background music; three short non-musical SFX cues. Three authentic interview excerpts. Newer statements are attributed narration because the original video downloads were unavailable. Export is 1080p; archive clips originate from 360p sources and are framed with dates.\n\nQC report: YouTube Ready/QC/qc_report.json.\n',encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
