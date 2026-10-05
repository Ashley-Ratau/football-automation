"""Anchor short visual cuts to measured narration character timestamps."""
from pathlib import Path
import csv,json,math,wave
P=Path(__file__).resolve().parent

def main():
    cfg=json.loads((P/'long_form_project.json').read_text())
    beats=json.loads((P/'visual_beats.json').read_text())
    timeline=[];offset=0.0
    for idx,s in enumerate(cfg['sections'],1):
        if s['type']=='insert':
            duration=float(s['end'])-float(s['start'])
            timeline.append(dict(file=s['file'],start=s['start'],duration=duration,label=s['name'],narration_anchor='Original pundit audio',section=s['name'],timeline_start=round(offset,4),kind='insert'))
            offset+=duration;continue
        raw=P/'assets/vo'/f'{idx:02d}_{s["name"]}_raw.wav'
        with wave.open(str(raw)) as w:duration=w.getnframes()/w.getframerate()
        a=json.loads(raw.with_suffix('.json').read_text())['alignment'];text=''.join(a['characters'])
        group=beats[s['name']];anchors=[]
        for beat in group:
            pos=text.find(beat['phrase'])
            if pos<0:raise ValueError(f'Missing anchor {s["name"]}: {beat["phrase"]}')
            anchors.append(a['character_start_times_seconds'][pos])
        anchors[0]=0
        if anchors!=sorted(anchors):raise ValueError('Anchors out of order: '+s['name'])
        s['broll']=[]
        for j,beat in enumerate(group):
            start=anchors[j];end=anchors[j+1] if j+1<len(group) else duration+.12
            span=end-start;n=max(1,math.ceil(span/(2.7 if idx==1 else 3.8)))
            choices=beat['shots']
            if len(choices)<n:raise ValueError(f'Need {n} shots for {s["name"]}: {beat["phrase"]}, have{len(choices)}')
            for k in range(n):
                src,seek=choices[k];d=span/n
                item=dict(file=f'assets/broll/{src}.mp4',start=seek,duration=round(d,6),label=f'{s["name"]}_{j:02d}_{k:02d}',narration_anchor=beat['phrase'])
                s['broll'].append(item)
                timeline.append(dict(item,section=s['name'],timeline_start=round(offset+start+k*d,4),kind='vo'))
        offset+=duration
    (P/'long_form_project.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    (P/'shot_timeline.json').write_text(json.dumps(timeline,indent=2),encoding='utf-8')
    with (P/'04 clip map.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(timeline[0]));wr.writeheader();wr.writerows(timeline)
    print(f'{len(timeline)} timeline shots; {offset:.3f} seconds planned')

if __name__=='__main__':main()
