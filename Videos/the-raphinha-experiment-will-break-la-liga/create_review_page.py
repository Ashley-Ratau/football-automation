"""Build the local review page from the final measured timeline."""
from pathlib import Path
import json,re,html
P=Path(__file__).resolve().parent
cfg=json.loads((P/'long_form_project.json').read_text())
report=json.loads((P/'final video/build_report.json').read_text())
reference=(P.parent/'barcelona-are-more-dangerous-than-you-think/START_HERE.html').read_text(encoding='utf-8')
css=re.search(r'<style>(.*?)</style>',reference,re.S).group(1)
chapters=[];offset=0
for s,item in zip(cfg['sections'],report['timeline']):
    chapters.append(dict(title=s.get('chapter',s.get('speaker','Pundit perspective')),start=round(offset,3)))
    offset+=item['duration']
video='final%20video/'+cfg['output_filename']
title=html.escape(cfg['title'])
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body><main>
<header class="header"><div><div class="eyebrow">Football Channel · Film review</div><h1>{title}</h1><div class="meta"><span>1080p · 30 fps</span><span>Liam narration</span><span>Three pundit perspectives</span><span>No captions</span></div></div><a class="download" href="{video}" download>Download video ↓</a></header>
<div class="viewer"><video id="film" controls preload="metadata" src="{video}"></video><div class="status" id="status">Loading the finished video…</div></div>
<div class="section-head"><h2>Explore the story</h2><p>Chapters follow the final edit.</p></div><nav class="chapters" id="chapters" aria-label="Video chapters"></nav>
<div class="section-head"><h2>Choose a thumbnail</h2><p>Raphinha. One idea. A clear focal point.</p></div><div class="gallery" id="gallery"></div>
<div class="section-head"><h2>Behind the video</h2><p>Research, narration and source context.</p></div><div class="files"><a class="file" href="03%20script.md">The script<span>Narration and pundit placements</span></a><a class="file" href="02%20research%20dossier.md">The evidence<span>Verified facts and analytical limits</span></a><a class="file" href="SOURCE_CREDITS.md">Source credits<span>Footage, pundits and original graphics</span></a></div>
<footer class="footer">Research through Sevilla, 19 September 2026. Tactical diagrams illustrate principles; they are not tracking data. Thumbnail artwork is an editorial design.</footer></main><script>
const chapters={json.dumps(chapters)},film=document.getElementById('film');
const clock=s=>`${{Math.floor(s/60)}}:${{String(Math.floor(s%60)).padStart(2,'0')}}`;
chapters.forEach(c=>{{let b=document.createElement('button');b.className='chapter';b.innerHTML=`<time>${{clock(c.start)}}</time>${{c.title}}`;b.onclick=()=>{{film.currentTime=c.start;film.play();}};document.getElementById('chapters').append(b);}});
film.onloadedmetadata=()=>document.getElementById('status').textContent=`Ready to review · ${{clock(Math.ceil(film.duration))}}`;
film.ontimeupdate=()=>document.querySelectorAll('.chapter').forEach((b,i)=>b.classList.toggle('active',film.currentTime>=chapters[i].start&&(i===chapters.length-1||film.currentTime<chapters[i+1].start)));
['EXPERIMENT','UNSTOPPABLE'].forEach((name,i)=>{{let path=`assets/thumbnail/thumbnail_${{String(i+1).padStart(2,'0')}}.png`;let card=document.createElement('article');card.className='card';card.innerHTML=`<a class="art" href="${{path}}"><img src="${{path}}" alt="Raphinha — ${{name}}"></a><div class="card-footer"><span>${{name}}</span><a href="${{path}}" download>Download ↓</a></div>`;document.getElementById('gallery').append(card);}});
</script></body></html>'''
(P/'START_HERE.html').write_text(page,encoding='utf-8')
print(P/'START_HERE.html')
