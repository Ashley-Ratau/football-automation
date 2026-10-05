from pathlib import Path
P=Path(__file__).resolve().parents[1]
(P/'06 asset acquisition log.md').write_text('''# Final asset log

Completed 3 October 2026. Archive downloads are 640x360; the delivery video is 1920x1080 and places them in dated frames. All source audio is muted under narration.

| Local source | Public source | Purpose |
|---|---|---|
| klopp_2022.mp4 | https://www.youtube.com/watch?v=Xhab3Sa5uDw | Two concise original statements and separate interview shots |
| klopp_cas_2020.mp4 | https://www.youtube.com/watch?v=0dx4xlJbLrY | Klopp's FFP principle; separately dated Guardiola archive |
| anfield_2019.mp4 | https://www.youtube.com/watch?v=co2xg4lLYjg | Final-day atmosphere, supporters, Klopp and squad |
| anfield_2022.mp4 | https://www.youtube.com/watch?v=kn5qaeZW96g | Second one-point title race |
| melwood_2019.mp4 | https://www.youtube.com/watch?v=HWAmk8gdevI | Squad preparation |
| city_haaland.mp4 | https://www.youtube.com/watch?v=HDXj6jiCeis | Haaland arrival and squad archive |

All source files reside in assets/broll. January 2025 and latest reaction are narrated with source-labelled graphics; accessible original video was unavailable. No substitute interview is represented as those events.

Original graphics: assets/graphics. Original non-musical SFX: assets/sfx, exactly three cues. No music track. Shot timestamps: production/shot_map.json. Insert timestamps: 04 clip map.csv. Voice metadata: assets/vo/*_raw.json.
''',encoding='utf-8')
(P/'07 edit brief.md').write_text('''# Final edit

Reference lessons applied: direct interview cold open, immediate stakes, a chronological evidence trail, a complication before the ending, and a callback to the 97-point season. No channel intro before the hook.

Ten narration sections match the latest Vinicius video's ElevenLabs Liam voice/model/settings and 1.15x pacing. Three concise original interview inserts replace narration. The picture uses a black/red/blue palette, point tables, gently moving original graphics, and dated archive frames. No general burned captions were requested.

Three short effects mark the first statistic, the 2020 transition, and publication of findings. No background music. The mix preserves narration gain. Final delivery loudness target: -16 LUFS, true peak -1.5 dB.

Export approximately 5 minutes 48 seconds; H.264/AAC, 1920x1080, 30fps. Archive source quality is 360p. Latest facts and appeal checked 3 October 2026. No upload or publication performed.

QC: complete decode, speech recognition of each narration opening and each interview excerpt, loudness/peak measurements, and representative visual frame inspection. A full listening audition was not available through the tools.
''',encoding='utf-8')
with (P/'02 research dossier.md').open('a',encoding='utf-8') as f:f.write('\n2021/22 graphic verified independently: City 93, Liverpool 92. Primary source: https://www.premierleague.com/en/news/2634049 .\n')
print('Final source and edit notes saved.')
