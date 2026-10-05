"""Original Raphinha-specific schematic scenarios; illustrations, not tracking data."""
from pathlib import Path
import json, subprocess
from PIL import ImageDraw, ImageFont
import tactics_art as art

P=Path(__file__).resolve().parent
FONT=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
# Attacking up the screen. Raphinha is index 0 and wears the highlighted 11.
SCENES={
 'central_reference': {'a':[(450,560),(1450,500),(900,730),(540,700)],'d':[(760,350),(1120,350),(1420,380),(650,520)],'moves':[('a',0,(970,395))],'ball':[(925,748),(970,430)],'note':'Wide origin becomes a central starting reference; role illustration.'},
 'pin_and_spin': {'a':[(990,415),(1450,500),(850,710),(480,500)],'d':[(990,345),(1220,345),(1430,380),(660,350)],'moves':[('a',0,(1110,245)),('d',0,(1020,355))],'ball':[(880,725),(1140,270)],'note':'Forward moves away from the ball before accelerating behind the marker.'},
 'drop_and_follow': {'a':[(980,370),(1460,500),(880,730),(500,470)],'d':[(975,300),(1230,325),(1430,385),(640,345)],'moves':[('a',0,(900,545)),('d',0,(925,470)),('a',3,(750,275))],'ball':[(910,745),(930,568),(775,300)],'note':'Following the dropping forward opens a channel for another runner.'},
 'hold_and_turn': {'a':[(980,370),(1460,500),(880,730),(500,470)],'d':[(975,300),(1230,325),(1430,385),(640,345)],'moves':[('a',0,(900,520)),('d',0,(970,310))],'ball':[(910,745),(930,545),(990,435)],'note':'Holding the line gives the dropping forward room to receive.'},
 'yamal_diagonal': {'a':[(880,430),(1450,520),(900,750),(480,480)],'d':[(870,340),(1120,350),(1410,390),(600,350)],'moves':[('a',0,(1080,250)),('d',2,(1400,475))],'ball':[(1480,540),(1110,278)],'note':'Right-side ball-holder finds a diagonal central run.'},
 'double_yamal': {'a':[(980,440),(1480,500),(900,750),(470,510)],'d':[(890,330),(1200,400),(1440,360),(630,340)],'moves':[('d',1,(1390,500)),('a',0,(1120,320))],'ball':[(1510,520),(1150,348)],'note':'Extra wide help vacates the inside passing lane.'},
 'third_man': {'a':[(940,450),(1450,500),(800,740),(490,510)],'d':[(890,340),(1170,330),(1420,350),(700,510)],'moves':[('a',0,(1070,255)),('a',2,(850,620))],'ball':[(830,760),(1480,520),(1100,280)],'note':'A third-player combination changes the angle of supply.'},
 'blind_side': {'a':[(740,385),(1470,450),(900,740),(490,530)],'d':[(920,345),(1170,345),(1420,350),(650,350)],'moves':[('a',0,(1030,220)),('d',0,(965,320))],'ball':[(1500,470),(1060,250)],'note':'Runner begins outside the defender’s immediate view and attacks the delivery.'},
 'press_curve': {'a':[(980,630),(1400,530),(900,820),(490,550)],'d':[(920,380),(1230,350),(1430,570),(610,510)],'moves':[('a',0,(1050,415)),('a',1,(1370,445))],'ball':[(950,402),(1260,375)],'note':'Curved central pressure shapes the opponent’s next pass.'},
 'compact_answer': {'a':[(1000,460),(1460,500),(900,760),(500,470)],'d':[(650,310),(850,310),(1050,310),(1250,310),(810,495),(1170,495)],'moves':[('d',4,(900,505)),('d',5,(1120,505)),('a',0,(1040,440))],'ball':[(930,785),(1490,522)],'note':'Compact opposition protects the central receiver and forces circulation.'},
 'transition_cost': {'a':[(1000,340),(1450,440),(900,720),(480,440)],'d':[(890,300),(1190,300),(760,600),(1150,570)],'moves':[('d',2,(680,855)),('d',3,(1150,825)),('a',2,(940,835))],'ball':[(1030,362),(1180,595),(1170,850)],'note':'A central turnover exposes space behind the attacking structure.'},
 'repeatable_routes': {'a':[(990,400),(1450,500),(870,745),(490,510)],'d':[(820,330),(1110,330),(1420,360),(660,400)],'moves':[('a',0,(1060,240)),('a',3,(570,330))],'ball':[(900,770),(520,535),(1090,268)],'note':'A different supply angle can reach the same central threat.'},
 'box_turn': {'a':[(1040,320),(1460,500),(870,700),(520,510)],'d':[(1020,260),(1260,310),(1400,385),(650,380)],'moves':[('a',0,(920,265)),('d',0,(1060,295))],'ball':[(900,720),(1067,339),(945,288),(920,125)],'note':'Schematic of receiving inside the box and changing the shooting angle; not measured Sevilla coordinates.'},
 'cross_arrival': {'a':[(1090,400),(1480,430),(880,720),(500,500)],'d':[(1000,300),(1250,325),(1400,365),(650,350)],'moves':[('a',0,(970,220)),('d',0,(1000,250))],'ball':[(1510,450),(995,235),(970,125)],'note':'Illustrative timing of a central arrival onto a right-side cross.'},
 'rodri_yamal_run': {'a':[(1040,445),(1450,465),(850,750),(470,500)],'d':[(880,325),(1170,325),(1390,350),(630,350)],'moves':[('a',0,(1120,215)),('a',2,(890,670))],'ball':[(880,770),(1480,485),(1140,242),(1000,125)],'note':'Schematic midfield-to-right-to-central-run sequence, reflecting the described third Sevilla goal without claiming tracking precision.'},
}

def frame(name,u):
    spec=SCENES[name];im=art.BASE.copy();d=ImageDraw.Draw(im)
    a=list(spec['a']);b=list(spec['d'])
    for team,i,end in spec['moves']:
        arr=a if team=='a' else b;start=arr[i]
        art.arrow(d,start,end,(239,193,92) if team=='a' and i==0 else (79,133,160),4)
        arr[i]=art.lerp(start,end,(u-.08)/.75)
    route=spec['ball']
    for start,end in zip(route,route[1:]):art.arrow(d,start,end,(129,114,69),3)
    for pos in b:art.player(d,pos,False)
    for i,pos in enumerate(a):
        art.player(d,pos,True)
        if i==0:
            x,y=pos;d.ellipse((x-36,y-36,x+36,y+36),outline=art.YELLOW,width=4)
            d.text((x,y),'11',font=FONT,anchor='mm',fill='white',stroke_width=1,stroke_fill=(10,25,35))
    q=max(0,min(.9999,(u-.25)/.65))*(len(route)-1);index=min(int(q),len(route)-2)
    x,y=art.lerp(route[index],route[index+1],q-index)
    d.ellipse((x-11,y-11,x+11,y+11),fill=art.YELLOW,outline='white',width=2)
    return im

if __name__=='__main__':
    out=P/'assets/broll';qa=P/'_tmp/tactics';qa.mkdir(parents=True,exist_ok=True)
    for name in SCENES:
        dest=out/f'tactics_{name}.mp4'
        if dest.exists():continue
        cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(dest)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        # 4 seconds of animation, with 1.5 seconds source headroom.
        for n in range(165):proc.stdin.write(frame(name,min(1,n/115)).tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError(name)
        frame(name,.65).save(qa/f'{name}.jpg',quality=90)
        print(name,flush=True)
    (P/'TACTICAL_SCENARIOS.json').write_text(json.dumps(SCENES,indent=2),encoding='utf-8')
