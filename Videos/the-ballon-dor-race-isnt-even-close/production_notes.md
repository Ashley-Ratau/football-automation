# The Ballon d'Or Race Isn't Even Close

Opinion piece arguing Lamine Yamal should win the 2026 Ballon d'Or (ceremony on 26 Oct 2026, London). It opens with his weakest number (1 goal and 0 assists at the World Cup) and argues that impact, titles and "gravity" outweigh Harry Kane's 61 goals. Runtime is 4:28, delivered as 1920x1080, 30 fps, H.264 with AAC at -14 LUFS.

**Final:** `final video/the-ballon-dor-race-isnt-even-close.mp4`

## Pipeline
1. `script_sections.json`: 8 sections and 738 words.
2. `produce_audio.py`: ElevenLabs narration with the Liam voice (`eleven_multilingual_v2`), including word timings. It also generates 3 original music cues (tension, case, verdict) and 4 sound effects (hit, whoosh, riser, stamp).
3. `gfx.py`: animated broadcast-style graphics (stat counters, Exhibit stamps, criteria list, voting window, odds board, Kane vs Yamal board, trophy cabinet, gravity tactical animation, date card, end card). They are rendered with alpha and placed over blurred, darkened footage.
4. `build.py`: the `PLAN` ties every shot to a word in the narration. Each footage shot gets a grade, a slow push-in and a vignette, and black-and-white is used for the "doubt" beats. Audio is mixed with music ducked under the voice and hits on graphics. Run `python build.py --plan` to print the timeline. Shots are cached per shot.
5. `contact.py`: contact sheets for picking shots and checking the final.

## Facts used (voting window 3 Aug 2025 to 19 Jul 2026)
- **Kane:** 61 goals in all competitions (36 Bundesliga, 14 Champions League, hat-trick in the DFB-Pokal final win over Stuttgart). Won the Bundesliga and the Pokal, and the Golden Shoe. Bayern went out to PSG in the Champions League semi-final. England lost the World Cup semi-final 2-1 to Argentina after leading.
- **Yamal:** 16 goals and 11 assists in La Liga, the most assists in the league. Shared the Zarra trophy. First hat-trick against Villarreal (4-1, 28 Feb). Won La Liga and La Liga Player of the Season.
- **Yamal at the World Cup:** 8 games, 1 goal (4-0 against Saudi Arabia), 0 assists. Player of the match in the 2-1 quarter-final against Belgium. Spain beat France 2-0 (Oyarzabal, Porro) and Argentina 1-0 after extra time (Ferran Torres). Argentina had 2 shots in the final.
- **Mbappé:** World Cup Golden Boot with 10 goals. Real Madrid won no trophies.
- **Dembélé:** reigning winner. PSG won the Champions League again (against Arsenal on penalties) and Ligue 1.
- **Criteria:** individual performance, then collective performance and titles, then class and fair play. Odds: Kane favourite and Yamal second (Oddschecker, 29 Sep 2026).
- Aged 19, Yamal would be the youngest winner ever.

## Footage (official channels; scorebugs and watermarks kept)
- **FIFA:** final (6HaHNYjnghE), semi-final against France (_cV8QcKp3GU), quarter-final against Belgium (VHoctq0AOg8, 8zNvahD-QS4), Saudi Arabia (j0BQN0nJ7mM), Mbappé Golden Boot (R6a86vVei8A).
- **SuperSport:** trophy lift (oqZrG38eftM).
- **FC Barcelona:** Best of Yamal 25/26 (cQQsgMpy2cA), 4-1 against Villarreal (3ehyky2UnRg), champions parade (VRCX4j2j23s).
- **FC Bayern:** all 36 Kane goals (8zVfkq04BK0), Pokal final (Cjfi6xRSfGE).

## Sources
ESPN, Al Jazeera and CNN nominee coverage; TNT Sports (criteria); beIN (voting closed 28 Sep); Bundesliga.com (Kane numbers, Golden Shoe); FC Barcelona (Player of the Season); Olympics.com (England semi-final, Champions League final); CBS (World Cup final); Oddschecker (odds); Goal (Dembélé, Ligue 1).
