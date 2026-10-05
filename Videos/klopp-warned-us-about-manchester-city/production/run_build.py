"""Run the existing Football Channel CLI with bounded encoding and a unity-gain SFX mix."""
from pathlib import Path
import importlib.util

path=Path(r'C:\Users\Wendy\Documents\Football Channel\work\football_long_form_automation.py')
spec=importlib.util.spec_from_file_location('football_automation',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
original=module.run
def run(command,*args,**kwargs):
    command=list(command)
    if 'ffmpeg' in Path(str(command[0])).name.lower():
        for i,a in enumerate(command):
            if isinstance(a,str) and 'amix=inputs=' in a and ':duration=first:dropout_transition=0' in a:
                command[i]=a.replace(':duration=first:dropout_transition=0',':duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.97')
        command[1:1]=['-threads','2']
        command[-1:-1]=['-threads','2']
    return original(command,*args,**kwargs)
module.run=run
# Visuals were already rendered at the validated delivery size and frame rate.
# Reuse them without a second full encode; the normal CLI still validates, muxes,
# assembles, mixes effects, exports, and generates its build report.
original_visual=module.render_broll_visual
def visual(project,section,duration,output,settings):
    items=section.get('broll',[])
    if len(items)==1 and items[0]['file'].startswith('assets/visuals/'):
        run([module.ffmpeg_exe(),'-y','-i',str(project/items[0]['file']),'-t',str(duration+.5),'-an','-c:v','copy',str(output)])
    else:original_visual(project,section,duration,output,settings)
module.render_broll_visual=visual
original_config=module.load_config
def config(project):
    cfg=original_config(project)
    for section in cfg.get('sections',[]):section['pause_after_seconds']=0
    return cfg
module.load_config=config
module.main()
