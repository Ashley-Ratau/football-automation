"""Passage-specific schematic clips. Not tracking data; no captions.
Each edit slot has its own scenario, paced to its exact existing duration.
"""
from pathlib import Path
import json,math,subprocess,shutil
from PIL import Image,ImageDraw
import imageio_ffmpeg
import create_tactics as art
P=Path(__file__).resolve().parent;OUT=P/'assets/broll';QA=P/'_tmp/tactics_v2_qa';QA.mkdir(parents=True,exist_ok=True)
# label: scene, interpretation. Every slot has a unique rendered file.
SPECS={
'early_damage_06_00':('compact','A compact defensive block protects central space while possession circulates outside.'),
'yamal_dilemma_08_00':('shoot','Wide attacker receives space, cuts inside and shoots toward goal.'),
'yamal_dilemma_10_00':('double','Second defender leaves an inside pocket to support the full-back.'),
'yamal_dilemma_15_00':('draw','Ball attracts two defenders to the right, exposing the weak-side lane.'),
'yamal_dilemma_15_01':('weak_run','Weak-side runner accelerates into the space while the ball travels diagonally.'),
'raphinha_space_03_00':('central_pass','A midfielder threads a central pass ahead of a forward run; schematic interpretation.'),
'raphinha_space_05_00':('timed_run','A forward delays, then accelerates behind the defensive line as the pass starts.'),
'raphinha_space_08_00':('split_choices','Two attackers diverge while the ball-carrier advances, forcing separate marking decisions.'),
'midfield_choices_01_00':('thread','Midfielder pauses, opens a passing angle and finds the central runner.'),
'midfield_choices_02_00':('one_two','A give-and-go: midfielder passes, advances, receives a return and finishes.'),
'midfield_choices_05_01':('pivot','Deep pivot shifts laterally to offer a clean outlet for the central defender.'),
'midfield_choices_06_00':('escape','Pivot turns away from approaching pressure and releases diagonally to a teammate.'),
'midfield_choices_06_01':('triangle','Three-player combination moves the ball through two passes around a pressing defender.'),
'midfield_choices_07_00':('post','Runner receives beyond pressure and shoots toward the near post; conceptual chance illustration.'),
'midfield_choices_09_00':('press_question','Two pressing defenders commit; a third attacker becomes the free passing outlet.'),
'flick_mechanism_01_00':('isolate','Full-back faces the wide attacker one-on-one with the ball.'),
'flick_mechanism_02_00':('helper','Midfielder moves across to support the full-back and makes a two-on-one.'),
'flick_mechanism_03_00':('pocket','The supporting defender has vacated an illuminated inside pocket.'),
'flick_mechanism_04_00':('exploit','A Barcelona runner enters that exact newly opened pocket.'),
'flick_mechanism_04_01':('step_hold','Centre-back steps toward the pocket while the adjacent defender holds, creating depth separation.'),
'flick_mechanism_06_00':('late_step','One defender reacts late as the forward and pass move through the lane.'),
'flick_mechanism_06_01':('restore','Defenders reconnect their line as attackers change direction for the next option.'),
'flick_mechanism_10_00':('repeat','Ball switches across the front of a block; the defence must shift again together.'),
'additional_weapons_03_00':('drive_create','Attacker drives toward a defender then slips the ball across to a supporting runner.'),
'additional_weapons_04_01':('box_arrival','Fresh central forward accelerates toward a wide delivery and meets the ball in the box.'),
'levante_warning_10_00':('backpass','A misplaced backpass is intercepted; the error is distinguished from a high-line failure.'),
'european_test_07_01':('elite_press','Opposition press closes two short outlets and forces the ball-holder to find the distant free man.'),
'opponents_choices_03_00':('relationships','Defenders track both the passer and runner together, closing the direct connection.'),
'opponents_choices_05_01':('double_cost','Double marking on the flank leaves another attacker free inside.'),
'opponents_choices_06_01':('turnover','Possession changes centrally and opponents counter into the space left behind.'),
'opponents_choices_10_03':('balanced','Defence pressures the ball while its back line shifts together and preserves its spacing.'),
'payoff_05_03':('many_routes','A short inside combination ends in a wide runner receiving an alternative passing route.'),
'payoff_09_00':('choice','Ball-carrier chooses between a central runner and a wide overlap, then finds the overlap.')}

def scene(kind):
 # Common starting map. Movements contain (team,index,end); ball route uses absolute points.
 A=[(1480,530),(1130,650),(760,660),(510,500),(950,780)]
 D=[(1430,350),(1190,430),(970,330),(700,340),(880,530)]
 moves=[]; route=[(1518,542)];hl=[];links=False;turn=False
 if kind in ['isolate','helper','pocket','exploit','step_hold','late_step','restore','double','draw','double_cost']:
  if kind=='isolate':moves=[('A',0,(1460,480)),('D',0,(1415,385))];route=[(1518,542),(1494,492)]
  elif kind in ['helper','double','draw','double_cost']:
   moves=[('D',1,(1360,490))];hl=[(1160,480,95)]
   if kind=='draw':moves += [('A',0,(1540,475)),('A',3,(570,400))];route=[(1518,542),(1570,487)]
   if kind=='double_cost':moves += [('A',1,(1160,430))];hl=[(1160,430,95)]
  else:
   D[1]=(1360,490);hl=[(1160,470,95)]
   if kind=='pocket':moves=[('A',0,(1460,505))];route=[(1518,542),(1493,518)]
   elif kind=='exploit':moves=[('A',1,(1160,450))]
   elif kind=='step_hold':A[1]=(1160,450);moves=[('D',2,(1090,405))];links=True
   elif kind=='late_step':A[1]=(1160,450);D[2]=(1090,405);moves=[('D',2,(1150,435)),('A',1,(1210,260))];route=[(1518,542),(1235,285)]
   elif kind=='restore':A[1]=(1210,260);moves=[('D',2,(1050,345)),('D',1,(1280,350)),('A',1,(1140,280)),('A',0,(1520,600))];links=True;route=[(1518,542),(1550,612)]
 elif kind in ['central_pass','timed_run','thread','post','weak_run']:
  D[4]=(875,725);A[2]=(760,600);route=[(795,614),(1190,280)];moves=[('A',1,(1160,255))];hl=[(1180,305,85)]
  if kind=='timed_run':A[1]=(1070,580);moves=[('A',1,(1210,265))];route=[(795,614),(1235,290)]
  if kind=='thread':moves += [('A',2,(820,570))];route=[(795,614),(850,584),(1190,280)]
  if kind=='weak_run':A[2]=(1450,540);A[3]=(500,600);moves=[('A',3,(620,300))];route=[(1480,553),(650,325)];hl=[(620,350,80)]
  if kind=='post':A[1]=(1140,370);moves=[('A',1,(1100,270))];route=[(795,614),(1130,292),(1055,128)]
 elif kind=='shoot':D[1]=(1150,300);moves=[('A',0,(1300,440))];route=[(1518,542),(1330,450),(960,135)];hl=[(1310,450,100)]
 elif kind in ['compact','repeat','balanced','relationships']:
  D=[(550,350),(800,350),(1050,350),(1300,350),(650,540),(950,540),(1250,540)];links=True
  moves=[('D',i,(x+90,y+10)) for i,(x,y) in enumerate(D)];route=[(1518,542),(985,792),(545,512)]
  if kind=='compact':moves=[('D',i,(x+35,y+5)) for i,(x,y) in enumerate(D)];route=[(1518,542),(985,792)]
  if kind=='balanced':moves=[('D',i,(x-100,y+35)) for i,(x,y) in enumerate(D)];moves += [('D',4,(610,595))];route=[(985,792),(545,512)]
  if kind=='relationships':moves=[('A',1,(1150,435)),('D',5,(950,635)),('D',6,(1160,480))];route=[(985,792),(795,674)];hl=[(1160,480,70),(950,635,70)]
 elif kind in ['pivot','escape','triangle','one_two','press_question','elite_press']:
  A=[(1440,510),(1140,510),(790,630),(530,450),(950,815)];D=[(1400,320),(1200,330),(1020,470),(660,370),(820,500)]
  if kind=='pivot':moves=[('A',2,(650,680))];route=[(985,827),(680,693)];hl=[(650,680,75)]
  elif kind=='escape':moves=[('D',4,(765,615)),('A',2,(680,645))];route=[(820,643),(710,658),(565,462)]
  elif kind=='triangle':moves=[('A',1,(1120,360)),('D',2,(910,570))];route=[(820,643),(1475,525),(1150,386)]
  elif kind=='one_two':D[2]=(955,360);moves=[('A',2,(1010,330))];route=[(820,643),(1175,525),(1040,357),(960,135)];hl=[(1040,390,80)]
  else:
   moves=[('D',2,(905,730)),('D',4,(810,685)),('A',3,(465,430))];route=[(985,827),(500,447)];hl=[(470,430,80)]
   if kind=='elite_press':moves += [('D',1,(1170,535))];route=[(985,827),(820,643),(500,447)]
 elif kind in ['split_choices','choice','many_routes','drive_create','box_arrival']:
  D[4]=(900,610);route=[(1518,542),(1180,340)];moves=[('A',1,(1150,315))]
  if kind=='split_choices':moves += [('A',3,(440,300)),('A',2,(810,560))];route=[(795,674),(845,574)];hl=[(450,350,80),(1150,350,80)]
  if kind=='choice':A[0]=(1340,580);moves=[('A',0,(1550,380)),('A',1,(1080,300))];route=[(795,674),(1580,407)]
  if kind=='many_routes':moves=[('A',0,(1530,355)),('A',1,(1150,430))];route=[(795,674),(985,792),(1180,455),(1560,378)]
  if kind=='drive_create':moves=[('A',0,(1360,450)),('D',1,(1340,390)),('A',1,(1090,320))];route=[(1518,542),(1390,464),(1120,345)]
  if kind=='box_arrival':moves=[('A',0,(1530,390)),('A',1,(1030,230))];route=[(1518,542),(1560,405),(1060,250),(970,135)]
 elif kind in ['backpass','turnover']:
  A=[(1450,530),(1100,490),(760,600),(520,470),(950,800)];D=[(1400,320),(1180,380),(960,400),(680,360),(850,650)]
  moves=[('D',4,(960,795)),('A',4,(1040,845))];route=[(795,614),(915,745),(1000,900)];turn=True;hl=[(930,760,80)]
  if kind=='turnover':moves=[('D',2,(1070,740)),('D',4,(700,800)),('A',1,(1120,640))];route=[(1130,505),(985,420),(1100,765)];hl=[(1060,725,90)]
 return A,D,moves,route,hl,links,turn

def frame(kind,u):
 im=art.BASE.copy();A,D,moves,route,hl,links,turn=scene(kind);d=ImageDraw.Draw(im)
 for x,y,r in hl:d.ellipse((x-r,y-r,x+r,y+r),fill=(33,48,47),outline=(114,101,54),width=2)
 for team,i,end in moves:
  positions=A if team=='A' else D;start=positions[i]
  art.arrow(d,start,end,(76,151,187) if team=='A' else (100,123,125),3)
  positions[i]=art.lerp(start,end,(u-.05)/.78)
 if links:
  for i in range(min(3,len(D)-1)):d.line((D[i],D[i+1]),fill=(68,106,109),width=3)
 for a,b in zip(route,route[1:]):art.arrow(d,a,b,(141,119,49),3)
 q=max(0,min(.9999,(u-.12)/.76))*(len(route)-1);i=min(int(q),len(route)-2) if len(route)>1 else 0
 ball=art.lerp(route[i],route[i+1],q-i) if len(route)>1 else route[0]
 for p in D:art.player(d,p,False)
 for p in A:art.player(d,p,True)
 x,y=ball;d.ellipse((x-12,y-12,x+12,y+12),fill=art.YELLOW,outline=(255,247,198),width=3)
 return im

def main():
 timeline=json.loads((P/'shot_timeline.json').read_text());mapping={};previews=[]
 for number,item in enumerate(timeline,1):
  if 'tactics_' not in item['file']:continue
  label=item['label'];kind,interpretation=SPECS[label];duration=item['duration'];name='tactics_v2_'+label+'.mp4';dest=OUT/name
  record={'file':'assets/broll/'+name,'start':0,'duration':duration,'shot':number,'section':item['section'],'narration_anchor':item['narration_anchor'],'scene':kind,'interpretation':interpretation,'previous_file':item['file'],'previous_start':item['start']};mapping[label]=record
  action_count=math.ceil(duration*30)+2
  count=action_count+36 # 1.2s final-pose tail for pipeline source headroom
  cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(count):proc.stdin.write(frame(kind,min(1,n/max(1,action_count-3))).tobytes())
  proc.stdin.close()
  if proc.wait():raise RuntimeError(name)
  strip=Image.new('RGB',(960,210));sd=ImageDraw.Draw(strip)
  for j,u in enumerate([.08,.48,.9]):
   im=frame(kind,u);im.thumbnail((320,180));strip.paste(im,(j*320,0))
  sd.text((8,185),f'{number:03d} {label} | {kind} | {duration:.2f}s',fill='white');previews.append(strip)
  print(f'{number:03d} {name}',flush=True)
 (P/'tactics_v2_mapping.json').write_text(json.dumps(mapping,indent=2))
 for page in range(math.ceil(len(previews)/7)):
  subset=previews[page*7:(page+1)*7];sheet=Image.new('RGB',(960,210*len(subset)))
  for i,im in enumerate(subset):sheet.paste(im,(0,i*210))
  sheet.save(QA/f'contact_{page+1:02d}.jpg',quality=94)
 print('COMPLETE',len(mapping),flush=True)
if __name__=='__main__':main()
