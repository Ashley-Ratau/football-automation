"""Use workspace football automation with project-specific audio and shot safeguards."""
import argparse, concurrent.futures, hashlib, importlib.util, json, math, subprocess, wave
from pathlib import Path

P=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('football_pipeline',r'C:\Users\Wendy\Documents\Football Channel\work\football_long_form_automation.py')
A=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(A)
_probe=A.media_probe
def accurate_probe(path):
    result=_probe(path)
    if path.name.endswith('_voice.aac'):
        raw=P/'assets'/'vo'/path.name.replace('_voice.aac','_raw.wav')
        if raw.exists():
            with wave.open(str(raw)) as w: result['duration']=w.getnframes()/w.getframerate()
    return result
A.media_probe=accurate_probe

def invoke(args):
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr[-3500:])
    return p

def voice(raw,output,settings):
    dur=A.media_probe(raw)['duration']/settings['voice_speed']
    invoke([A.ffmpeg_exe(),'-y','-i',raw,'-af',
        f"atempo={settings['voice_speed']},loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=in:d=0.03,afade=t=out:st={dur-0.03}:d=0.03",
        '-ar','44100','-ac','2','-c:a','aac','-b:a','192k',output])

def visual(project,section,duration,output,settings):
    folder=output.parent/(output.stem+'_clips');folder.mkdir(exist_ok=True)
    items=section['broll']
    coverage=sum(x['duration'] for x in items)
    if coverage < duration-0.1:
        raise RuntimeError(f'{section["name"]}: shot list does not cover narration ({coverage}/{duration}); looping refused')
    tasks=[]; elapsed=0
    for i,item in enumerate(items):
        frames=round((elapsed+item['duration'])*30)-round(elapsed*30)
        if frames<1: continue
        path=folder/f'clip_{i+1:03d}.mp4'
        tasks.append((path,item,frames))
        elapsed+=item['duration']
    def render(task):
        path,item,frames=task
        recipe=json.dumps([item,frames],sort_keys=True)
        digest=hashlib.sha256(recipe.encode()).hexdigest()
        receipt=path.with_suffix('.sha256')
        if path.exists() and receipt.exists() and receipt.read_text()==digest:return path
        vf=item.get('vf','')
        if vf: vf+=','
        vf+='scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30'
        invoke([A.ffmpeg_exe(),'-y','-ss',item['start'],'-i',project/item['file'],
            '-an','-vf',vf,'-frames:v',frames,'-c:v','libx264','-preset','veryfast','-crf','18',
            '-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360',path])
        receipt.write_text(digest)
        return path
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: paths=list(pool.map(render,tasks))
    concat=folder/'concat.txt';concat.write_text('\n'.join("file '"+x.as_posix()+"'" for x in paths))
    invoke([A.ffmpeg_exe(),'-y','-f','concat','-safe','0','-i',concat,'-c','copy',output])
    print(f'Rendered {section["name"]}: {len(paths)} meaningful shots',flush=True)

def music(source,music,output,settings):
    duration=A.media_probe(source)['duration']
    normalized=music.with_name('music_normalized.wav')
    if not normalized.exists() or normalized.stat().st_size < 1000:
        invoke([A.ffmpeg_exe(),'-y','-i',music,'-af','loudnorm=I=-30:TP=-5:LRA=7','-ar','44100','-ac','2',normalized])
    # Silence the added score throughout pundit excerpts, preserving their own audio.
    cfg=json.loads((P/'long_form_project.json').read_text(encoding='utf-8-sig'))
    elapsed=0.0; windows=[]
    for index,section in enumerate(cfg['sections'],1):
        segment=P/'_tmp'/f'segment_{index:02d}_{section["name"]}.mp4'
        segment_duration=A.media_probe(segment)['duration']
        if section['type']=='insert':
            windows.append(f'between(t,{elapsed:.6f},{elapsed+segment_duration:.6f})')
        elapsed+=segment_duration
    gate = ('volume=0:enable=\'' + '+'.join(windows) + '\',') if windows else ''
    filters=(f'[1:a]{gate}afade=t=in:d=1,afade=t=out:st={duration-3}:d=3[m];'
      '[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=false,volume=-0.5dB[a]')
    invoke([A.ffmpeg_exe(),'-y','-i',source,'-stream_loop','-1','-i',normalized,'-filter_complex',filters,
        '-map','0:v:0','-map','[a]','-t',duration,'-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-ac','2','-movflags','+faststart',output])

A.ffmpeg_exe=lambda: 'ffmpeg'
A.process_voice=voice
A.render_broll_visual=visual
A.mix_music=music
if __name__=='__main__':
    args=argparse.Namespace(project=str(P),model_id='eleven_multilingual_v2 / Liam bu5eKETbFKC8G702EAU4',skip_tts=True)
    A.build_project(args)
