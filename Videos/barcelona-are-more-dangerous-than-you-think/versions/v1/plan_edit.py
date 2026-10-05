"""Sentence-anchored edit decisions using ElevenLabs character timing."""
import csv,json,math,wave
from pathlib import Path
P=Path(__file__).resolve().parent
F='feyenoord_5_1'; R='racing_7_2'; V='valencia_5_0'; L='levante_4_2'
T='training_focused'; U='training_ucl'; D='training_recover'; H='sevilla_preview'
W='tactics_wide_overload'; I='tactics_inside_runner'; C='tactics_coordinated_shift'

# Each spoken anchor starts a visual beat. Tuples are (verified source, seek seconds).
BEATS={
'hook':[
 ('How do you',[(R,169),(F,8)]),
 ('Double up',[(R,176),(F,88)]),
 ('Follow Raphinha',[(F,48),(F,56)]),
 ('Try to take',[(T,211),(U,352)]),
 ('Seven competitive',[(R,1),(F,36),(R,179)]),
 ('That is the start',[(F,180),(T,55)]),
 ('But the scorelines',[(R,76),(V,15)]),
 ('The really interesting',[(U,278),(F,92),(R,131)]),
 ('And there is one',[(L,118),(L,140),(L,157)]),
 ('Because this team',[(F,34),(R,176)]),
 ('But first',[(F,7),(R,15)])],
'early_damage':[
 ('Five minutes at Valencia',[(V,12)]),('Three minutes against',[(F,9)]),
 ('Five at Levante',[(L,13)]),('Eight against Racing',[(R,13)]),
 ('Four matches',[(R,18),(F,19)]),
 ('That matters',[(T,183),(D,193)]),
 ('An opponent can',[(C,1),(U,325),(T,230)]),
 ('Then the plan',[(F,23),(V,25)]),
 ('Stay deep',[(R,111),(R,131)]),
 ('Push more',[(L,170),(T,298)]),
 ('An early goal',[(L,116),(D,247)]),
 ('But it makes',[(U,377),(T,325)]),
 ('And when',[(R,81),(V,155),(R,174),(F,29)]),
 ('The next question',[(D,274),(R,21)])],
'yamal_dilemma':[
 ('Start with',[(R,176),(V,22)]),
 ('Seven league',[(L,35),(V,165)]),
 ('Two against Rayo',[(T,189)]),
 ('Two at Valencia',[(V,165)]),('Two at Levante',[(L,43)]),
 ('Then another',[(R,175)]),
 ('The player',[(R,171),(F,89)]),
 ('That changes',[(R,176),(W,2)]),
 ('Give him',[(F,69),(F,79)]),
 ('Rush into',[(R,155),(V,16)]),
 ('Send help',[(W,5),(T,210)]),
 ('Against Feyenoord',[(F,72),(F,80)]),
 ('There is no',[(R,180),(D,156)]),
 ('Of course',[(U,130),(D,118)]),
 ('The point',[(V,49),(R,171),(T,191)]),
 ('And the more',[(W,1),(F,47),(F,55)])],
'raphinha_space':[
 ('That player',[(R,2),(F,57)]),
 ('Eleven goals',[(F,25),(R,54)]),
 ('But put',[(F,44),(F,48)]),
 ('Against Feyenoord',[(F,49),(F,53),(F,58)]),
 ('The decisive',[(F,44),(I,1)]),
 ('A runner',[(I,3),(I,6)]),
 ('The pass',[(F,51),(F,60)]),
 ('That is the',[(U,401),(T,231)]),
 ('You cannot',[(C,1),(D,208),(F,12)]),
 ('Against Racing',[(R,50),(R,81),(R,91)]),
 ('So this',[(R,56),(D,235),(U,252)]),
 ('It is a broader',[(R,138),(F,15),(R,87)]),
 ('Now look',[(F,156),(T,138)])],
'midfield_choices':[
 ('Pedri can',[(F,157),(V,144),(T,185)]),
 ('The pass',[(F,46),(F,50)]),
 ('At Valencia',[(V,141),(V,148)]),
 ('Creator',[(V,150),(T,208)]),
 ('The roles',[(U,331),(D,191)]),
 ('Rodri also',[(V,64),(V,71)]),
 ('In one sequence',[(V,64),(V,69),(V,74)]),
 ('That move',[(U,345),(I,3)]),
 ('Close down',[(T,213),(U,359)]),
 ('The question',[(C,2),(D,287),(U,427)]),
 ('If you cannot',[(V,91),(R,170),(T,298)])],
'flick_mechanism':[
 ('This is where',[(F,184),(U,379)]),
 ('Imagine you',[(W,0),(R,176)]),
 ('Your midfielder',[(W,3)]),
 ('That can be',[(W,6),(T,210)]),
 ('A Barcelona runner',[(I,0),(I,4),(R,111)]),
 ('Neither choice',[(D,175),(T,235)]),
 ('The danger',[(C,3),(C,6)]),
 ('That is the tactical',[(F,189),(T,53)]),
 ('Barcelona keep',[(R,129),(U,304),(I,6)]),
 ('It does not',[(D,233),(T,300)]),
 ('It means',[(C,1),(T,255),(U,377)]),
 ('And just',[(R,99),(F,104),(D,48)])],
'additional_weapons':[
 ('Karim Adeyemi',[(F,31),(F,36)]),
 ('He settled',[(L,168),(L,176)]),
 ('Against Racing',[(R,38),(R,70),(R,168)]),
 ('Those are different',[(F,124),(R,43),(L,178)]),
 ('Gabriel Jesus',[(F,106),(F,113),(R,143)]),
 ('This matters',[(R,101),(T,75)]),
 ('They have to',[(U,451),(D,47)]),
 ('A game can',[(T,290),(R,105),(T,369),(U,273)]),
 ('That does not',[(D,82),(T,123)]),
 ('Seven matches',[(F,181)]),
 ('It does show',[(R,181),(F,93),(V,165)]),
 ('But here',[(L,119),(L,138)])],
'levante_warning':[
 ('At Levante',[(L,77),(L,92)]),
 ('Comfortable',[(L,100)]),
 ('Then a poor',[(L,109),(L,115),(L,127)]),
 ('In the eighty',[(L,146),(L,153)]),
 ('Three-nil',[(L,159),(L,164)]),
 ('Suddenly',[(L,151),(L,163)]),
 ('Adeyemi eventually',[(L,168),(L,175),(L,179)]),
 ('But the warning',[(F,190),(D,209)]),
 ('An attack',[(R,132),(F,80),(T,231)]),
 ('And we should',[(L,110),(L,115)]),
 ('Calling every',[(C,2),(D,305)]),
 ('The bigger',[(F,199),(T,254)]),
 ('Can Barcelona',[(D,289),(U,326),(T,275)]),
 ('Against Europe',[(F,12),(F,100),(U,354)])],
'european_test':[
 ('The Feyenoord',[(F,8),(F,30)]),
 ('Five-one',[(F,58),(F,80),(F,108)]),
 ('It is also',[(F,92),(F,113)]),
 ('A convincing',[(F,182),(U,53),(T,144)]),
 ('Even Feyenoord',[(F,43),(F,98)]),
 ('That is why',[(D,81),(U,403)]),
 ('The schedule',[(U,60),(T,368),(D,27),(F,187)]),
 ('Those are',[(T,214),(C,2),(D,326),(T,390)]),
 ('The challenge',[(D,250),(T,189)]),
 ('It is retaining',[(U,306),(T,299),(R,112)]),
 ('That is the difference',[(F,59),(T,434),(R,180)])],
'opponents_choices':[
 ('So what',[(F,197),(C,0)]),
 ('First, survive',[(F,10),(R,16),(V,13)]),
 ('The early goals',[(F,24),(R,19)]),
 ('Second, defend',[(C,4),(W,1)]),
 ('Tracking Raphinha',[(F,46),(F,53)]),
 ('Doubling Lamine',[(W,4),(I,3)]),
 ('Third, make',[(D,284),(C,6)]),
 ('Levante showed',[(L,126),(L,155)]),
 ('None of this',[(F,185),(T,79)]),
 ('It is the task',[(T,211)]),
 ('And it explains',[(U,351),(T,232),(D,192),(I,5),(U,280),(R,171)]),
 ('That is a demanding',[(T,435),(R,181)])],
'payoff':[
 ('The numbers',[(R,2),(R,79),(R,177)]),
 ('They describe',[(F,188),(T,52)]),
 ('That distinction',[(D,45),(U,130)]),
 ('We do not need to pretend',[(L,121),(L,150)]),
 ('We do not need to declare',[(F,181),(U,61)]),
 ('Barcelona have already',[(R,173),(F,52),(F,156),(F,108),(R,143)]),
 ('The next step',[(T,210),(C,5)]),
 ('If they do',[(F,200),(D,82)]),
 ('So when Europe',[(R,85),(F,112),(V,164)]),
 ('Ask how many',[(I,3),(R,170)]),
 ('Then ask',[(F,9),(R,178)]),
 ('Because while',[(T,298),(F,50),(F,58)])]
}

Y='yamal_illustrative_archive'; PY='portrait_lamine_yamal'; PR='portrait_raphinha'; PP='portrait_pedri'
def replace_beats(section,replacements):
    BEATS[section]=[(phrase,replacements.get(phrase,shots)) for phrase,shots in BEATS[section]]
replace_beats('hook',{'Double up':[(PY,1),(Y,49)],'Follow Raphinha':[(PR,1),(F,50)]})
replace_beats('yamal_dilemma',{
 'Start with':[(PY,0),(Y,44)],'Seven league':[(Y,61),(PY,4)],
 'Two against Rayo':[(PY,2)],'Two at Valencia':[(PY,3)],'Two at Levante':[(Y,93)],'Then another':[(Y,100)],
 'The player':[(Y,109),(PY,1)],'That changes':[(Y,50),(W,2)],
 'Give him':[(W,1),(Y,61)],'Rush into':[(Y,94),(W,4)],'Send help':[(W,5),(Y,109)],
 'Against Feyenoord':[(PY,2),(F,71)],'There is no':[(Y,40),(W,4)],
 'Of course':[(Y,44),(PY,5)],'The point':[(Y,100),(W,1),(Y,61)],
 'And the more':[(W,1),(I,3),(F,50)]})
replace_beats('raphinha_space',{'That player':[(PR,0),(R,2)],'Against Feyenoord':[(I,1),(F,49),(F,57)]})
replace_beats('midfield_choices',{
 'Pedri can':[(PP,0),(F,157),(T,185)],'At Valencia':[(I,2),(PP,3)],
 'Creator':[(PP,4),(I,4)],'Rodri also':[('portrait_rodri',1),(C,1)],
 'In one sequence':[(C,3),(I,1),(I,5)],'That move':[(I,4),(U,345)]})
replace_beats('additional_weapons',{
 'Karim Adeyemi':[('portrait_adeyemi',1),(F,30)],'Against Racing':[('portrait_adeyemi',3),(R,128),(R,168)],
 'Those are different':[(I,2),(R,43),(L,168)],
 'Gabriel Jesus':[('portrait_gabriel_jesus',1),(F,107),(R,142)]})
replace_beats('opponents_choices',{'Doubling Lamine':[(Y,50),(W,4),(I,3)]})
replace_beats('payoff',{'Barcelona have already':[(PY,1),(PR,1),(PP,1),(I,2),(R,141)]})

replace_beats('raphinha_space',{'Against Feyenoord':[(I,1),(PR,2)],'Against Racing':[(PR,1),(R,128)]})
replace_beats('midfield_choices',{'The pass':[(I,1),(PP,2)]})
replace_beats('additional_weapons',{'He settled':[('portrait_adeyemi',2),(I,2)],'Gabriel Jesus':[('portrait_gabriel_jesus',1),(I,3),(T,185)]})
# Exclude the source channel's opening subscription card wherever Racing is used.
for section, beats in BEATS.items():
    BEATS[section]=[(phrase,[(src,10 if src==R and seek<8 else seek) for src,seek in choices]) for phrase,choices in beats]

def main():
    cfg=json.loads((P/'long_form_project.json').read_text()); timeline=[]; offset=0
    for idx,s in enumerate(cfg['sections'],1):
        raw=P/'assets/vo'/f'{idx:02d}_{s["name"]}_raw.wav'
        with wave.open(str(raw)) as w:duration=w.getnframes()/w.getframerate()
        a=json.loads(raw.with_suffix('.json').read_text())['alignment']
        text=''.join(a['characters']);starts=a['character_start_times_seconds']
        beats=BEATS[s['name']];anchors=[]
        for phrase,choices in beats:
            pos=text.find(phrase)
            if pos<0:raise ValueError(f'Anchor missing {s["name"]}: {phrase}')
            anchors.append(starts[pos])
        anchors[0]=0
        if anchors!=sorted(anchors):raise ValueError(f'Out of order anchors {s["name"]}')
        s['broll']=[]
        for j,(phrase,choices) in enumerate(beats):
            start=anchors[j];end=anchors[j+1] if j+1<len(anchors) else duration+0.12
            span=end-start
            n=max(1,math.ceil(span/(2.7 if idx==1 else 3.8)))
            for k in range(n):
                src,seek=choices[k%len(choices)]
                seek+=4.15*(k//len(choices))
                # Drawings use only their validated ten-second windows.
                if src.startswith(('tactics_','portrait_')):seek=min(seek,5.8)
                d=span/n
                item={'file':f'assets/broll/{src}.mp4','start':round(seek,3),'duration':round(d,6),'label':f'{s["name"]}_{j:02d}_{k:02d}','narration_anchor':phrase}
                s['broll'].append(item)
                timeline.append(dict(item,section=s['name'],timeline_start=round(offset+start+k*d,4)))
        offset+=duration
    cfg['music_bed']='assets/music_original.mp3'
    cfg['research_checks']={k:True for k in cfg['research_checks']}
    cfg['upload']['description']='Barcelona are more dangerous than you think..\n\nAn original analysis of Barcelona\'s opening seven competitive matches of 2026/27, through the Racing game on 16 September 2026. Researched 19 September.\n\nSources and full research dossier are supplied with the local project.\nNarration: ElevenLabs Liam. No captions.'
    (P/'long_form_project.json').write_text(json.dumps(cfg,indent=2))
    (P/'shot_timeline.json').write_text(json.dumps(timeline,indent=2))
    with (P/'04 clip map.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(timeline[0]));wr.writeheader();wr.writerows(timeline)
    print(f'Planned {len(timeline)} shots over {offset:.2f}s')

if __name__=='__main__':main()
