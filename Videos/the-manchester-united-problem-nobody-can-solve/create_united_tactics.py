"""Original Manchester United tactical illustrations; schematic, not tracking data."""
from pathlib import Path
import subprocess
from PIL import ImageDraw, ImageFont
import tactics_art as art

P=Path(__file__).resolve().parent
FONT=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
SCENES={
'compact_442':{'a':[(820,470),(1120,470),(720,610),(980,620),(1240,610),(960,770)],'d':[(650,300),(930,300),(1210,300),(1460,360)],'moves':[('a',0,(845,430)),('a',1,(1095,430))],'ball':[(960,785),(980,640),(1110,485)]},
'transition_release':{'a':[(800,470),(1110,470),(610,620),(980,610),(1350,620),(960,770)],'d':[(690,330),(940,320),(1190,330),(1400,420)],'moves':[('a',2,(670,250)),('a',4,(1260,245)),('a',3,(1000,350))],'ball':[(960,790),(990,620),(1270,275)]},
'low_block_problem':{'a':[(850,500),(1080,500),(620,590),(960,570),(1310,590),(960,760)],'d':[(650,300),(850,300),(1050,300),(1250,300),(760,420),(1140,420)],'moves':[('a',3,(980,450)),('a',2,(650,500)),('a',4,(1280,500))],'ball':[(960,780),(640,610),(680,520)]},
'right_overload':{'a':[(820,480),(1080,500),(620,610),(1020,610),(1390,580),(960,770)],'d':[(720,310),(950,310),(1190,320),(1410,360)],'moves':[('d',3,(1320,470)),('a',4,(1420,390)),('a',3,(1230,440))],'ball':[(960,790),(1040,630),(1260,460),(1420,410)]},
'rest_defence_gap':{'a':[(820,420),(1110,420),(600,500),(990,520),(1380,500),(960,720)],'d':[(760,320),(1050,310),(1300,350),(920,610)],'moves':[('d',3,(720,840)),('a',0,(850,510)),('a',1,(1080,510))],'ball':[(1000,535),(920,635),(740,815)]},
'game_state_balance':{'a':[(820,470),(1100,470),(630,610),(980,600),(1340,610),(960,760)],'d':[(680,310),(920,300),(1160,310),(1390,380)],'moves':[('a',0,(850,430)),('a',1,(1070,430)),('a',3,(1000,460))],'ball':[(960,780),(985,620),(1000,490)]}}

def frame(name,u):
 spec=SCENES[name];im=art.BASE.copy();d=ImageDraw.Draw(im);a=list(spec['a']);b=list(spec['d'])
 for team,i,end in spec['moves']:
  arr=a if team=='a' else b;start=arr[i];art.arrow(d,start,end,(239,193,92) if team=='a' else (79,133,160),4);arr[i]=art.lerp(start,end,max(0,min(1,(u-.08)/.75)))
 route=spec['ball']
 for start,end in zip(route,route[1:]):art.arrow(d,start,end,(129,114,69),3)
 for pos in b:art.player(d,pos,False)
 for i,pos in enumerate(a):
  art.player(d,pos,True)
  if i in (0,1,3):
   x,y=pos;d.ellipse((x-34,y-34,x+34,y+34),outline=art.YELLOW,width=3)
 q=max(0,min(.9999,(u-.25)/.65))*(len(route)-1);idx=min(int(q),len(route)-2);x,y=art.lerp(route[idx],route[idx+1],q-idx);d.ellipse((x-11,y-11,x+11,y+11),fill=art.YELLOW,outline='white',width=2)
 d.text((960,1010),'SCHEMATIC ILLUSTRATION — NOT TRACKING DATA',font=FONT,anchor='mm',fill=(220,225,228));return im

if __name__=='__main__':
 out=P/'assets'/'broll';qa=P/'_tmp'/'tactics';qa.mkdir(parents=True,exist_ok=True)
 for name in SCENES:
  dest=out/f'tactics_{name}.mp4';cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(dest)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(165):proc.stdin.write(frame(name,min(1,n/115)).tobytes())
  proc.stdin.close()
  if proc.wait():raise RuntimeError(name)
  frame(name,.65).save(qa/f'{name}.jpg',quality=90);print(name,flush=True)
