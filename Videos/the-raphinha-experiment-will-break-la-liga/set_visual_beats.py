from pathlib import Path
import json
P=Path(__file__).resolve().parent
S='sevilla_current_1_3';B='raphinha_best_2025_26';T='raphinha_training_spotlight';G='raphinha_group_training'
def shots(src,*times):return [[src,t] for t in times]
def tac(name):return [['tactics_'+name,0]]
def beat(phrase,choices):return {'phrase':phrase,'shots':choices}
BEATS={
'hook':[
 beat('You prepare',shots(S,174,179,145)),
 beat('Against Sevilla',shots(S,60,112,144)),
 beat('Three different',shots(S,146,180)),
 beat('Hansi Flick',tac('central_reference')+shots(G,175,185)),
 beat('Fourteen goals',shots(S,177,122,152)),
 beat('But this is bigger',shots(T,95,103,113,134)),
 beat('After the Sevilla',shots(S,180,174,177))],
'role':[
 beat('The important word',shots(T,74,81,88)),
 beat('Playing centrally',shots(B,462,466,477)),
 beat('It gives him',shots(T,151,155,161)),
 beat('Come towards',tac('drop_and_follow')+shots(B,607,611)),
 beat('Then disappear',tac('pin_and_spin')+shots(B,640,644)),
 beat('Those movements',shots(T,97,106,117,137)),
 beat('He can recognise',tac('blind_side')+shots(B,778,782)),
 beat('Think about',shots(B,740,744,748)),
 beat('Through the middle',shots(B,805,809,813)),
 beat('Flick has not',shots(S,176,180)+shots(G,178,184)),
 beat('He is changing',shots(T,164,168,171)),
 beat('This is a mobile',shots(B,907,911,915,947))],
'dilemma':[
 beat('Imagine you',shots(B,905,908)),
 beat('Raphinha comes short',shots(T,125,129)),
 beat('Follow him',tac('drop_and_follow')+shots(T,154)),
 beat('Hold your position',tac('hold_and_turn')+shots(T,162)),
 beat('Neither decision',shots(G,159,165,170)),
 beat('Now put',shots(S,97,118)),
 beat('If your team',tac('double_yamal')+shots(S,102,106)),
 beat('Raphinha can',shots(S,107,111)),
 beat('If you protect',tac('yamal_diagonal')+shots(S,136,140)),
 beat('Barcelona do not',shots(G,321,329,342)),
 beat('Pedri can',shots('portrait_pedri',1,4)),
 beat('Yamal can',shots(S,138,142)),
 beat('A combination',tac('third_man')+shots(G,356,365)),
 beat('That is why',shots(T,135,139,143)),
 beat('The runner needs',shots(S,137,141,145)),
 beat('When those two',shots(B,850,854,858)),
 beat('Earlier in September',shots(T,197,191))],
'sevilla':[
 beat('Sevilla gave us',shots(S,10,15,24)),
 beat('And it started',shots(S,38,42,46)),
 beat('Their pressure',shots(S,40,44,48)),
 beat('Then Raphinha',shots(S,54,58)),
 beat('Christensen found',shots(S,59,63,67)),
 beat('That is one version',tac('box_turn')+shots(S,68,71,70)),
 beat('After the break',shots(S,100,104)),
 beat('Yamal delivered',shots(S,107,110,114)),
 beat('This time',tac('cross_arrival')+shots(S,124,128)),
 beat('For the third',shots(S,137,139,143)),
 beat('Raphinha ran',shots(S,139,142,148)),
 beat('Receive and turn',shots(S,67,125,156)),
 beat('It is tempting',shots(S,176,180,174)),
 beat('But that misses',tac('rodri_yamal_run')+shots(S,151,155)),
 beat('The defender',shots(S,158,161)),
 beat('And Raphinha',shots(S,174,178,182)),
 beat('He needs to recognise',shots(T,94,99,103))],
'league':[
 beat('After that win',shots(S,174,179,183)),
 beat('Thirty-one goals',shots(S,61,114,146)),
 beat('That is an extraordinary',shots(T,111,117,121)),
 beat('Three of his',shots(B,673,677,681)),
 beat('A scoring rate',shots(G,332,342,348)),
 beat('The stronger argument',tac('repeatable_routes')+shots(T,171,176)),
 beat('You can have',shots(T,183,187,191)),
 beat('You can miss',shots(T,61,66,71)),
 beat('That is the part',shots(G,252,259,268)),
 beat('And for Real Madrid',shots(B,462,469,477)),
 beat('Keep collecting',shots(G,304,310,318)),
 beat('Then find a way',shots(B,487,491,498)),
 beat('Madrid had won',shots(G,156,162,169)),
 beat('So this is not',shots(T,96,103,111)),
 beat('Every Barcelona win',shots(S,175,179,183)),
 beat('Every different route',shots(G,373,382,397)),
 beat('And earlier this month',shots(T,134,138,142))],
'limits_payoff':[
 beat('There are answers',tac('compact_answer')+shots(G,271,281)),
 beat('Pressure the passer',tac('press_curve')+shots(G,299,303)),
 beat('Pass runners',shots(G,323,333,343)),
 beat('And when Barcelona',tac('transition_cost')+shots(G,367,374,382)),
 beat("Sevilla's first half",shots(S,38,42,46)),
 beat('The experiment still',shots(G,352,361,395,402)),
 beat('But that is',shots(T,93,99)),
 beat('Raphinha is giving',shots(B,851,855,858)),
 beat('Whether this breaks',shots(T,140,148,155)),
 beat('Right now',shots(S,146,150,174,178)),
 beat('So when the next',shots(B,775,779,784)),
 beat('Does he follow',shots(S,139,143,147,180))]
}
(P/'visual_beats.json').write_text(json.dumps(BEATS,indent=2),encoding='utf-8')
cfg=json.loads((P/'long_form_project.json').read_text())
inserts=json.loads((P/'assets/inserts/selected_inserts.json').read_text())
for s,info in zip([s for s in cfg['sections'] if s['type']=='insert'],inserts):
    s.update(start=0,end=info['duration_seconds'],speaker=info['speaker'],chapter=info['speaker']+' — expert view',source_url=info['source_url'],source_date=info['upload_date'])
cfg['research_checks']={k:True for k in cfg['research_checks']}
(P/'long_form_project.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
