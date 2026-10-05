from pathlib import Path
import json,subprocess,csv
P=Path(__file__).resolve().parents[1]
cfg=json.loads((P/'long_form_project.json').read_text(encoding='utf-8'))
cuts={'cold_open':('warning','klopp_2022',286.0,288.95,'JURGEN KLOPP / OCTOBER 2022 / THIS IS ANFIELD'), 'cas_interview':('cas','klopp_cas_2020',34.2,43.32,'JURGEN KLOPP / JULY 2020 / ESPN UK'), 'financial_ceiling':('ceiling','klopp_2022',304.7,311.65,'JURGEN KLOPP / OCTOBER 2022 / THIS IS ANFIELD')}
rows=[]
for s in cfg['sections']:
    if s['type']!='insert':continue
    name,source,start,end,label=cuts[s['name']]; dest=P/'assets/inserts'/f'{name}.mp4'
    vf=f"scale=1536:864,pad=1920:1080:192:78:color=0x11161D,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{label}':x=192:y=958:fontsize=29:fontcolor=0xA2ABB5,fps=30"
    r=subprocess.run(['ffmpeg','-y','-loglevel','error','-threads','2','-ss',str(start),'-i',str(P/'assets/broll'/f'{source}.mp4'),'-t',str(end-start),'-vf',vf,'-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-c:a','aac','-ar','44100','-ac','2',str(dest)],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr)
    s['end']=round(float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(dest)],text=True)),2)
    rows.append([s['name'],f'assets/broll/{source}.mp4',start,end,'Original audio; complete short statement; no VO/music overlay'])
with (P/'04 clip map.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['section','source_asset','source_in_seconds','source_out_seconds','edit_note']);w.writerows(rows)
(P/'long_form_project.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding='utf-8')
script=['# Klopp Warned Us About Manchester City','Final narration and insert order. Facts checked 3 October 2026. Liam VO at 1.15x. No background music.']
for s in cfg['sections']:
    script.append('## '+s['name'].replace('_',' ').title())
    script.append(s['text'] if s['type']=='vo' else f"[ORIGINAL INTERVIEW: {s['file']}, 0–{s['end']:.2f}s. Narration stops.]" )
(P/'03 script.md').write_text('\n\n'.join(script)+'\n',encoding='utf-8')
with (P/'02 research dossier.md').open('a',encoding='utf-8') as f:
    f.write('\n## Final production verification\n\nCity\'s appeal verified against the club\'s own statement: https://www.mancity.com/news/club/manchester-city-lodge-appeal-63926534 . Lodged 1 October 2026.\n\nFinal uses three concise original excerpts: October 2022 warning (286.0–288.95), July 2020 financial-fair-play principle (34.2–43.32), October 2022 financial comparison (304.7–311.65). Timings inspected against local transcript and frames. The Mallorca joke and newest response use attributed narration and original graphics because accessible original footage was not acquired. No fabricated dialogue.\n\nResearch gates: scoreline checked where mentioned (City beat Liverpool in the only 2018-19 league defeat); record/points checked using Liverpool and Premier League records. Match number and player availability: N/A, no such claims in script. Source URLs recorded.\n')
print('Final input manifest ready; three concise interview clips; music disabled.')
