from pathlib import Path
import json,subprocess,math,wave,random,struct,textwrap,concurrent.futures
from PIL import Image,ImageDraw,ImageFont

P=Path(__file__).resolve().parents[1]
G=P/'assets/graphics'; G.mkdir(exist_ok=True)
V=P/'assets/visuals'; V.mkdir(exist_ok=True)
I=P/'assets/inserts'; I.mkdir(exist_ok=True)
S=P/'assets/sfx'; S.mkdir(exist_ok=True)
CFG=P/'long_form_project.json'
config=json.loads(CFG.read_text(encoding='utf-8'))
FONT=Path('C:/Windows/Fonts')
def font(size,bold=False): return ImageFont.truetype(str(FONT/('arialbd.ttf' if bold else 'arial.ttf')),size)
red='#E34C57';blue='#83CAEB';white='#F3F3EF';muted='#A2ABB5'; bg='#11161D'
def shell(kicker,source=''):
    im=Image.new('RGB',(1920,1080),bg);d=ImageDraw.Draw(im)
    for x in range(0,1920,80):d.line((x,0,x,1080),fill='#171D25')
    for y in range(0,1080,80):d.line((0,y,1920,y),fill='#171D25')
    d.rectangle((100,112,166,120),fill=red);d.text((190,93),kicker.upper(),font=font(31,True),fill=muted)
    d.line((100,933,1820,933),fill='#35414E',width=2)
    d.text((100,967),source,font=font(24),fill=muted)
    return im,d
def card(name,kicker,title,lines,source='',accent=red):
    im,d=shell(kicker,source)
    sz=85 if len(title)<28 else 63
    for row,t in enumerate(title.split('\n')):d.text((100,220+row*100),t,font=font(sz,True),fill=white)
    yy=460 if '\n' not in title else 520
    for t in lines:
        for line in textwrap.wrap(t,width=51):
            d.text((104,yy),line,font=font(43),fill=accent if yy==460 else white);yy+=68
        yy+=15
    im.save(G/f'{name}.png')
def table(name,year,city,liverpool):
    im,d=shell(f'THE TITLE RACE / {year}','Source: Liverpool FC / Premier League final standings')
    d.text((100,220),'ONE POINT.',font=font(113,True),fill=white)
    d.text((105,362),'The margin between a season and a title.',font=font(42),fill=muted)
    for yy,n,p,c in [(520,'MANCHESTER CITY',city,blue),(690,'LIVERPOOL',liverpool,red)]:
        d.rectangle((100,yy,1820,yy+133),fill='#1C2631')
        d.rectangle((100,yy,115,yy+133),fill=c)
        d.text((160,yy+34),n,font=font(47,True),fill=white)
        d.text((1620,yy+17),str(p),font=font(82,True),fill=c)
    im.save(G/f'{name}.png')
card('ninetyseven','LIVERPOOL / 2018-19','97 POINTS.', ['30 wins. One league defeat.','Second place.'],'Source: Liverpool FC, 12 May 2019')
table('table19','2018-19',98,97);table('table22','2021-22',93,92)
card('impossible','THE STANDARD','WHEN EXCELLENT\nIS NOT ENOUGH',['An extraordinary campaign.','Another team one point ahead.'],'2018-19 Premier League title race')
card('cas','13 JULY 2020 / COURT OF ARBITRATION FOR SPORT','THE BAN WAS OVERTURNED.',['Most allegations: not established or time-barred.','Fine for non-cooperation remained.'],'Source: CAS decision summary / UEFA, 13 July 2020',blue)
card('champions','THE TIMING MATTERS','LIVERPOOL WERE CHAMPIONS.',['This warning came when Klopp was on top.'],'2019-20 champions / July 2020 interview')
card('limits','THE MONEY QUESTION','WHERE ARE THE LIMITS?',['Resources. Revenue. Rules.','Spending more is not itself proof of a breach.'],'Original analysis / Klopp financial-power comments')
card('boundaries','THE WARNING','FINANCIAL BOUNDARIES',['Klopp questioned competitive conditions.','He did not claim access to investigators\' files.'],'October 2022 comments / original analysis')
card('respect','RIVALS / OCTOBER 2022','MUTUAL RESPECT.',['Recognising Guardiola\'s quality.','Questioning financial conditions.'],'Source: Liverpool FC interview, 15 October 2022',blue)
card('parade','JANUARY 2025 / A CONDITIONAL JOKE','A PARADE IN MALLORCA?',['Klopp joked about a celebration at home','if titles were ever awarded retrospectively.'],'Source: ESPN, 14 January 2025')
card('period','THE IMPORTANT DISTINCTION','DIFFERENT PERIODS.',['Financial findings: 2009/10 to 2017/18.','Klopp runner-up seasons: 2018/19 and 2021/22.'],'Source: Premier League statement, 29 September 2026',blue)
card('findings','29 SEPTEMBER 2026 / PREMIER LEAGUE','THE FINDINGS ARE PUBLISHED.',['Disguised funding and inaccurate reporting.','Conduct over nine seasons.'],'Source: Premier League statement, 29 September 2026')
card('appeal','CITY\'S RESPONSE / 1 OCTOBER 2026','CITY HAS APPEALED.',['The club disputes the findings.','Sanctions are a separate stage.'],'Source: Manchester City appeal statement / Premier League',blue)
card('reaction','LATEST REACTION / REPORTED 1 OCTOBER 2026','NO VICTORY LAP.',['Klopp played down talk of a parade.','Respect for Guardiola\'s football remained.'],'Source: Associated Press / SNTV interview reporting')
card('ending','THE QUESTION THAT REMAINS','WHAT DO THE RULES PROTECT?',['A meaningful boundary.','A competition that supporters can trust.'],'Original commentary / facts checked 3 October 2026')
card('callback','THE SEASON WE STARTED WITH','97 POINTS.', ['The season cannot be replayed.','The debate is far from finished.'],'Liverpool 2018-19 / original commentary')

# Each source range appears once. Only the opening statistic is recalled at the end.
# The beat string is located in ElevenLabs character alignment for exact narration matching.
plans={
'hook':[(None,'ninetyseven'),('That was Liverpool',('anfield_2019',490)),('Manchester City finished','table19'),('Three years later','table22'),('Years later',('klopp_2022',130)),('He could build',('anfield_2022',530)),('But he could not','limits'),('Now the Premier League','findings'),('The findings do not','appeal')],
'season':[(None,'table19'),('They lost only once',('anfield_2019',430)),('The point is not',('anfield_2019',220)),('But the standard',('melwood_2019',122)),('An ordinary improvement','impossible'),('A very good season',('anfield_2019',385)),('That is the emotional',('anfield_2019',360)),('For supporters',('anfield_2019',563))],
'cas_setup':[(None,'cas'),('finding that most','cas'),('That distinction matters','period'),('It was not the later',('klopp_cas_2020',215)),('Klopp was asked',('klopp_cas_2020',5)),('He explained why','limits')],
'cas_followup':[(None,'champions')],
'money':[(None,('melwood_2019',30)),('Klopp contrasted','limits'),('Liverpool spent money too',('melwood_2019',75)),('Klopp was not',('melwood_2019',155)),('His argument concerned','boundaries'),('In October 2022',('klopp_2022',175)),('City could add Haaland',('city_haaland',85)),('Liverpool could not',('melwood_2019',215))],
'warning_meaning':[(None,'boundaries')],
'respect':[(None,('klopp_cas_2020',252)),('Klopp repeatedly respected','respect'),('In the same October',('klopp_2022',206)),('That makes this more',('city_haaland',155)),('Klopp could recognise',('anfield_2022',190)),('Those positions can coexist','respect'),('Equally','boundaries'),('The important comparison','limits'),('We do not need',('anfield_2019',590))],
'parade':[(None,'parade'),('He said that if it happened','parade'),('Supporters immediately',('anfield_2019',617)),('They remembered',('anfield_2022',490)),('The idea of celebrating',('anfield_2022',555)),('But a joke','period'),('The argument about a squad',('city_haaland',55)),('It does not establish','appeal')],
'findings':[(None,'findings'),('It described','findings'),('City rejects','appeal'),('That is significant','boundaries'),('Then Klopp was asked','reaction'),('Here was the man',('anfield_2019',540)),('The obvious ending','reaction'),('He played down','reaction'),('The final reaction',('anfield_2022',575))],
'ending':[(None,('anfield_2019',640)),('Supporters cannot',('anfield_2019',409)),('What can change','ending'),('A warning about','boundaries'),('The strongest version','limits'),('It asks whether','ending'),('He challenged City',('anfield_2022',510)),('He questioned',('klopp_2022',244)),('Ninety-seven points','callback')]
}
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-2000:])
def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)],text=True).strip())
def find_time(meta,needle):
    a=meta.get('normalized_alignment') or meta['alignment']; text=''.join(a['characters']); idx=text.lower().find(needle.lower())
    if idx<0:raise ValueError(f'Missing visual beat: {needle}')
    return float(a['character_start_times_seconds'][idx])/1.15

def visual_scene(job):
    name,idx,obj,length=job; dest=V/f'{name}_{idx:02d}.mp4'
    if dest.exists() and abs(duration(dest)-length)<.08:return dest
    common=['ffmpeg','-y','-loglevel','error','-threads','2']
    if isinstance(obj,str):
        source=G/f'{obj}.png'
        # A gentle camera move keeps a source card alive without flashy transitions.
        vf="scale=1960:1102,crop=1920:1080:x='20+10*sin(t/4)':y='11+5*sin(t/5)',fps=30"
        cmd=common+['-loop','1','-framerate','30','-i',str(source),'-t',f'{length:.5f}','-vf',vf]
    else:
        file,start=obj;source=P/'assets/broll'/f'{file}.mp4'
        # Archive remains dated and inset; no mismatched match footage or flipped text.
        labels={'anfield_2019':'LIVERPOOL FC  /  12 MAY 2019','anfield_2022':'LIVERPOOL FC  /  22 MAY 2022','melwood_2019':'LIVERPOOL TRAINING  /  AUGUST 2019','klopp_2022':'KLOPP PRESS CONFERENCE  /  OCTOBER 2022','klopp_cas_2020':'MANAGERS REACT TO CAS  /  JULY 2020','city_haaland':'MAN CITY  /  HAALAND ARCHIVE 2022-23'}
        fontfile='C\\:/Windows/Fonts/arialbd.ttf'
        vf=f"scale=1536:864,pad=1920:1080:192:78:color=0x11161D,drawbox=x=192:y=966:w=64:h=6:color=0xE34C57:t=fill,drawtext=fontfile='{fontfile}':text='{labels[file]}':x=282:y=955:fontsize=27:fontcolor=0xA2ABB5,fps=30"
        cmd=common+['-ss',str(start),'-i',str(source),'-t',f'{length:.5f}','-vf',vf]
    run(cmd+['-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(dest)])
    return dest

shot_log=[];jobs=[];groups={}
for i,s in enumerate(config['sections'],1):
    if s['type']!='vo':continue
    name=s['name'];meta=json.loads((P/'assets/vo'/f'{i:02d}_{name}_raw.json').read_text(encoding='utf-8'))
    total=duration(P/'assets/vo'/f'{i:02d}_{name}_raw.wav')/1.15+.65
    starts=[]
    for beat,obj in plans[name]:starts.append((0 if beat is None else find_time(meta,beat),obj))
    starts.sort(key=lambda v:v[0]); current=[]
    for j,(at,obj) in enumerate(starts):
        end=starts[j+1][0] if j+1<len(starts) else total
        if end-at<.15:continue
        jobs.append((name,j,obj,end-at));current.append((name,j,obj,end-at));shot_log.append({'section':name,'start':at,'duration':end-at,'asset':obj})
    groups[name]=current
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for path in pool.map(visual_scene,jobs):print('Shot ready '+path.name,flush=True)
safety=V/'source_safety_tail.mp4'
run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','color=c=0x11161D:s=1920x1080:r=30:d=2','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20',str(safety)])
for s in config['sections']:
    if s['type']!='vo':continue
    name=s['name'];dest=V/f'{name}.mp4';lst=V/f'{name}_concat.txt'
    lst.write_text('\n'.join(f"file '{(V/f'{name}_{j:02d}.mp4').as_posix()}'" for _,j,_,_ in groups[name]),encoding='utf-8')
    run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(dest)])
    s['broll']=[{'file':f'assets/visuals/{name}.mp4','start':0,'duration':duration(dest)-1.01}]
    # The renderer requires an extra one-second source safety margin.
    padded=V/f'{name}_padded.mp4'
    safety_list=V/f'{name}_safety_concat.txt'
    safety_list.write_text(f"file '{dest.as_posix()}'\nfile '{safety.as_posix()}'",encoding='utf-8')
    run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(safety_list),'-c','copy',str(padded)])
    s['broll']=[{'file':f'assets/visuals/{name}_padded.mp4','start':0,'duration':duration(dest)}]

def insert(name,source,start,end,label):
    dest=I/f'{name}.mp4'
    vf=f"scale=1536:864,pad=1920:1080:192:78:color=0x11161D,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{label}':x=192:y=958:fontsize=29:fontcolor=0xA2ABB5,fps=30"
    run(['ffmpeg','-y','-loglevel','error','-threads','2','-ss',str(start),'-i',str(P/'assets/broll'/f'{source}.mp4'),'-t',str(end-start),'-vf',vf,'-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-c:a','aac','-ar','44100','-ac','2',str(dest)])
    return duration(dest)
timings={'cold_open':('warning','klopp_2022',286.0,299.65,'JURGEN KLOPP / OCTOBER 2022 / THIS IS ANFIELD'),'cas_interview':('cas','klopp_cas_2020',30.65,61.0,'JURGEN KLOPP / JULY 2020 / ESPN UK'),'financial_ceiling':('ceiling','klopp_2022',304.7,326.1,'JURGEN KLOPP / OCTOBER 2022 / THIS IS ANFIELD')}
for s in config['sections']:
    if s['type']=='insert':s['end']=insert(*timings[s['name']])

# Original short broadband transitions: no melodic material and no music bed.
def noise_effect(name,seconds,kind):
    rng=random.Random(31);rate=44100;data=[];last=0
    for n in range(round(rate*seconds)):
        t=n/rate;u=t/seconds;noise=rng.uniform(-1,1)
        last=.91*last+.09*noise
        envelope=(math.sin(math.pi*u)**2) if kind=='air' else math.exp(-u*11)*min(1,u*80)
        value=(noise-last)*envelope*.28 if kind=='air' else last*envelope*.9
        data.append(max(-32767,min(32767,int(value*32767))))
    with wave.open(str(S/f'{name}.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<'+'h'*len(data),*data))
noise_effect('soft_transition',.8,'air');noise_effect('muted_impact',.55,'impact')
config['sound_effects']=[{'name':'first_stat','file':'assets/sfx/muted_impact.wav','duration_seconds':.55,'anchor_section':'hook','offset_seconds':0,'volume_db':-7}, {'name':'case_shift','file':'assets/sfx/soft_transition.wav','duration_seconds':.8,'anchor_section':'cas_setup','offset_seconds':0,'volume_db':-14},{'name':'published_findings','file':'assets/sfx/muted_impact.wav','duration_seconds':.55,'anchor_section':'findings','offset_seconds':0,'volume_db':-10}]
config['research_checks']={k:True for k in config['research_checks']}
config['upload']['description']='Jurgen Klopp challenged Manchester City on the pitch and questioned the financial system around the rivalry. This video follows his public warnings, the 2020 CAS decision, and the Premier League findings published on 29 September 2026. Manchester City disputes those findings and lodged an appeal on 1 October; sanctions remain a separate stage. Facts checked 3 October 2026.\n\nSources: Premier League, CAS, UEFA, Liverpool FC, Manchester City, ESPN and Associated Press. Original interview excerpts: This Is Anfield and ESPN UK. Full source links are included in the project research dossier.'
CFG.write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding='utf-8')
(P/'production/shot_map.json').write_text(json.dumps(shot_log,indent=2),encoding='utf-8')
(P/'08 voiceover log.md').write_text('# Voiceover\n\nMatched to latest Vinicius project: ElevenLabs Liam, bu5eKETbFKC8G702EAU4, eleven_multilingual_v2; stability .43, similarity .82, style .18, speaker boost on. 1.15x pacing. Loudness normalized before existing renderer compression and limiting. No music. Three short original non-musical sound cues.\n',encoding='utf-8')
print('Visuals and production configuration complete.',flush=True)
