"""Editable, original schematic tactical animations. Generic illustrations, not tracking data.
Run: python create_tactics.py. Pillow frames pipe into imageio-ffmpeg's bundled binary.
"""
from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
W,H,FPS,DURATION=1920,1080,30,10
OUT=Path(__file__).resolve().parent/'assets'/'broll'
OUT.mkdir(parents=True,exist_ok=True)
NAVY=(7,19,31); LINE=(64,100,107); YELLOW=(255,214,84)

def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def lerp(a,b,t): return tuple(a[i]+(b[i]-a[i])*ease(t) for i in range(2))
def base():
 im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
 for x in range(140,1780,205): d.rectangle((x,125,x+204,955),fill=(10+(x//205)%2*2,34+(x//205)%2*3,40+(x//205)%2*3))
 d.rounded_rectangle((140,125,1780,955),radius=5,outline=LINE,width=3)
 d.rectangle((625,125,1295,365),outline=LINE,width=3)
 d.rectangle((790,125,1130,225),outline=LINE,width=3)
 d.rectangle((855,95,1065,125),outline=LINE,width=3)
 d.arc((790,190,1130,530),0,180,fill=LINE,width=3)
 d.ellipse((954,287,966,299),fill=LINE)
 d.arc((765,760,1155,1150),180,360,fill=LINE,width=3)
 return im
BASE=base()
def arrow(d,a,b,color,width=5):
 d.line((a,b),fill=color,width=width)
 ang=math.atan2(b[1]-a[1],b[0]-a[0]); r=20
 p=[b,(b[0]-r*math.cos(ang-.5),b[1]-r*math.sin(ang-.5)),(b[0]-r*math.cos(ang+.5),b[1]-r*math.sin(ang+.5))]
 d.polygon(p,fill=color)
def player(d,p,barca=True):
 x,y=p;r=27
 d.ellipse((x-r+3,y-r+6,x+r+3,y+r+6),fill=(3,13,20))
 if barca:
  d.ellipse((x-r,y-r,x+r,y+r),fill=(24,103,195),outline=(111,175,240),width=2)
  d.pieslice((x-r,y-r,x+r,y+r),-90,90,fill=(187,39,70))
  d.ellipse((x-r,y-r,x+r,y+r),outline=(155,181,212),width=2)
 else: d.ellipse((x-r,y-r,x+r,y+r),fill=(222,230,221),outline=(255,255,250),width=2)
def make_frame(kind,t):
 im=BASE.copy();d=ImageDraw.Draw(im)
 if kind==1:
  # Wide attacker holds the ball; a second marker drifts wide and opens a pocket.
  attackers=[(1500,500),(1110,680),(740,615),(550,445),(1040,430)]
  defenders=[(1460,360),lerp((1210,440),(1380,460),(t-1)/3),(990,325),(730,330),(515,335),(900,530)]
  if t>3:
   overlay=Image.new('RGBA',(W,H));od=ImageDraw.Draw(overlay)
   od.rounded_rectangle((1120,350,1290,610),radius=70,fill=(255,211,70,int(25*ease((t-3)/2))))
   im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
  if t>1: arrow(d,(1210,440),(1380,460),(119,143,144),3)
  if t>4: arrow(d,(1110,660),(1200,435),YELLOW,5)
  ball=(1537,518)
 elif kind==2:
  run=lerp((1150,660),(1160,310),(t-1.5)/4)
  attackers=[(1500,500),run,(740,615),(520,460),(950,720)]
  defenders=[(1460,360),(1350,435),(980,320),(720,330),(515,335),(890,640)]
  arrow(d,(1150,640),(1160,320),(82,147,170),4)
  if t>2: arrow(d,(755,590),(1160,338),YELLOW,4)
  ball=lerp((772,594),(1190,332),(t-3)/2.7)
 else:
  shift=ease((t-1)/5)
  start=[(580,340),(800,320),(1040,320),(1280,340),(670,520),(950,490),(1230,520)]
  defenders=[(x+shift*140,y+shift*20) for x,y in start]
  attackers=[lerp((1450,600),(1510,420),(t-1)/5),lerp((1150,710),(1220,460),(t-2)/5),lerp((650,690),(820,575),(t-1)/5),(490,475),(980,790)]
  # A translucent connected block exposes coordinated defensive shifting.
  for i,j in [(0,1),(1,2),(2,3),(4,5),(5,6),(0,4),(3,6)]:d.line((defenders[i],defenders[j]),fill=(52,83,90),width=3)
  if t>1:
   arrow(d,(1450,590),(1510,440),(88,151,178),4)
   arrow(d,(1150,690),(1220,480),(88,151,178),4)
  ball=lerp((1014,788),(1545,432),(t-2)/4)
 for p in defenders:player(d,p,False)
 for p in attackers:player(d,p,True)
 x,y=ball; d.ellipse((x-11,y-11,x+11,y+11),fill=YELLOW,outline=(255,247,198),width=3)
 return im

def render(kind,name):
 path=OUT/name
 cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for n in range(FPS*DURATION):
  im=make_frame(kind,n/FPS)
  if n==180:im.save(OUT/f'{path.stem}_preview.jpg',quality=95)
  p.stdin.write(im.tobytes())
 p.stdin.close()
 if p.wait():raise RuntimeError('ffmpeg failed')
 print(path,flush=True)
if __name__=='__main__':
 for kind,name in [(1,'tactics_wide_overload.mp4'),(2,'tactics_inside_runner.mp4'),(3,'tactics_coordinated_shift.mp4')]:render(kind,name)

