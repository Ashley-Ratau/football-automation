from pathlib import Path
import json
P=Path(__file__).resolve().parent
cfg=json.loads((P/'long_form_project.json').read_text())
credits=['# Source credits','', 'Research cutoff: the Sevilla match on 19 September 2026; researched 20 September.','', '## Pundit excerpts','']
inserts=json.loads((P/'assets/inserts/selected_inserts.json').read_text())
for x in inserts:
    credits.append(f'- {x["speaker"]}, ESPN, uploaded {x["upload_date"]}: {x["source_url"]}. Source excerpt {x["start_seconds"]:.2f}–{x["end_seconds"]:.2f} seconds. Original audio; no narrator underneath.')
credits+=['','## B-roll','', 'Archive footage illustrates Raphinha’s qualities; it is not presented as footage of the current Sevilla match. The named Sevilla goal sequences use the current match source or clearly schematic diagrams. Original source marks are retained.','']
used={Path(x['file']).stem for s in cfg['sections'] if s['type']=='vo' for x in s['broll']}
for name in sorted(used):
    meta=P/'assets/broll'/f'{name}.info.json'
    if meta.exists():
        d=json.loads(meta.read_text(encoding='utf-8'))
        credits.append(f'- {d.get("title",name)} — {d.get("channel",d.get("uploader",""))}; uploaded {d.get("upload_date","unknown")}; {d.get("webpage_url","")}. Local source: `assets/broll/{name}.mp4`.')
credits+=['- Pedri identity shot: animated official club portrait, reused from the approved Barcelona project; https://www.fcbarcelona.com/en/football/first-team/players/70486/pedro-gonzalez-lopez .', '', '## Original elements','', '- Fifteen distinct tactical scenarios, designed for the corresponding narration. Highlighted number 11 identifies the Raphinha role. These are conceptual illustrations, not measured tracking data.', '- Narration: ElevenLabs Liam, voice ID bu5eKETbFKC8G702EAU4, multilingual v2, natural speed.', '- Original instrumental music generated with ElevenLabs Music for the preceding approved Barcelona production and reused here. Added music is muted during pundit inserts.', '- Two photoreal editorial thumbnail composites generated with the built-in image tool using an official Raphinha identity reference. See assets/thumbnail/PROVENANCE.md.', '', '## Publication status', '', 'This is a local review master. It has not been uploaded for YouTube checks; source attribution does not establish footage licensing or guarantee clearance.']
(P/'SOURCE_CREDITS.md').write_text('\n'.join(credits),encoding='utf-8')
script=['# The Raphinha Experiment Will Break La Liga','', 'Final narration and insert order. No added captions.','']
for s in cfg['sections']:
    script.append('## '+s.get('chapter',s['name']))
    if s['type']=='vo':script.append(s['text'])
    else:script.append(f'Original {s["speaker"]} excerpt, {s["source_date"]}, {s["end"]:.2f} seconds. {s["source_url"]}. Full source transcript and excerpt boundaries are in assets/inserts.')
    script.append('')
(P/'03 script.md').write_text('\n\n'.join(script),encoding='utf-8')
(P/'01 idea brief.md').write_text('# Idea brief\n\nTitle: '+cfg['title']+'\n\nA fresh analysis of Raphinha as a mobile central forward under Flick, using the three Sevilla goals as the central case study and explaining the implications for La Liga without declaring the title race finished.\n',encoding='utf-8')
(P/'07 edit brief.md').write_text('# Edit brief\n\nNarration-aligned short cuts, three original-audio pundit inserts, first at approximately 33 seconds. Per-section narration normalization; score muted during inserts. Fifteen distinct tactical scenarios illustrate specific mechanisms. No burned-in narration captions. Final 1080p30, chaptered HTML review, two solo Raphinha thumbnail options.\n',encoding='utf-8')
(P/'08 voiceover log.md').write_text('# Voiceover\n\nElevenLabs Liam, multilingual v2, natural speed. Measured narration: 323.918367 seconds (5:23.92). Script hashes and complete character timings preserved next to each WAV. See NARRATION_QC.md.\n',encoding='utf-8')
(P/'05 clip sourcing plan.md').write_text('# Clip sourcing\n\nCurrent Sevilla match footage supports the named match case study. Official club training and the 2025/26 Raphinha compilation provide illustrative archive b-roll. Three English ESPN excerpts add distinct external observations. Fifteen original tactical scenarios explain specific actions. Exact URLs and dates: SOURCE_CREDITS.md. Exact shot timing: 04 clip map.csv.\n',encoding='utf-8')
(P/'06 asset acquisition log.md').write_text('# Asset acquisition\n\nFresh assets were acquired into this project using yt-dlp. See assets/broll_manifest.json, assets/inserts/selected_inserts.json, and source metadata adjacent to downloaded footage. Rejected prior Raphinha project excluded. Only reusable production code and original music came from the successful Barcelona project.\n',encoding='utf-8')
print('Script, evidence and source-credit documents packaged.')
