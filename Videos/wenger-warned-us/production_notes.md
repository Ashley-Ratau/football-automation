# Wenger Knew

A quote-driven "vindication" documentary in the style of the Mourinho reference (see memory: reference-mourinho-was-right). Arsène Wenger's own words from 1996 to 2020 are cut against the 29 September 2026 Premier League commission ruling on Manchester City.

**Final file:** `final video/wenger-knew.mp4`

## Title options
1. **Wenger Knew. Nobody Listened.** (recommended)
2. Arsène Wenger Tried To Warn Us
3. Wenger Was Right About Man City All Along

**Thumbnail concept:** two faces on black. Wenger in front, sharp. Pep or the City owners behind, tinted red. The words **"HE" / "KNEW"** sit either side.

## Pipeline
- `script.json` lists the sections in order: `vo` (narration), `quote` (a real soundbite, with `from`/`to` words resolved by `quotes.py`) and `card` (a quote card).
- `produce_audio.py` creates the ElevenLabs Liam narration only. No AI music is used.
- `transcribe.py` runs faster-whisper word timestamps on the 360p copies. The timing is the same in the HD copies in `assets/clips/hd/`.
- `gfx.py` makes the date tags, italic text overlays, quote cards and title/end cards.
- `build.py` has the PLAN (shots tied to narration words) and CUTAWAYS (over long soundbites). It applies a desaturated or black-and-white grade, a slow zoom-in and grain. It mixes the music (ducked under voice, and further under soundbites), adds burned captions and exports. Run `python build.py --plan` to see the timeline.

## Fact sheet (all verified)
- **PL statement, 29 Sep 2026:** City were found guilty of breaches over the seasons 2009/10–2017/18. They used "'sham' contracts" with commercial partners. Revenues were inflated and costs reduced "by more than £900 million". City "made concerted efforts to stop and frustrate the PL investigation". Sanctions will be decided at a separate hearing. Source: premierleague.com statement.
- Ornstein reported the verdict on 25 Sep 2026. City lodged an appeal on 2 Oct 2026 (Sky Sports News). A final outcome may not come until 2027 (Al Jazeera, Insider Sport).
- **Wenger soundbites (video):**
  - Jan 2016, Hayters: about doping in sport. The video says explicitly that he was talking about drugs.
  - 1996, Sky Sports Retro: "You cannot buy success just by buying big names".
  - Sky Sports Retro: the new stadium and investors (Chelsea, then City).
  - Sept 2009, ITN: "I wish always my former players to be happy".
  - Aug 2011, Telegraph: "Ideally I want Samir Nasri to stay".
  - Dec 2017, Guardian: "no petrol, but ideas / petrol and ideas".
  - Jan 2018: "I respect Man United because they generate the money... with their own resources".
  - Feb 2020, Laureus (Sky News/Beanyman): "sport is basically to win by respecting the rules... you cannot let that unpunished".
- **Etihad quote, July 2011** (print, via The Guardian, reproduced by GiveMeSport): "if the financial fair play is to have a chance, the sponsorship has to be at the market price. It cannot be doubled, tripled or quadrupled".
- **Etihad deal:** July 2011, reported at about £400m over 10 years, covering shirt, stadium and campus.
- **Transfers:** Adebayor (£25m) and Touré (£16m) in July 2009. Clichy (£7m) in July 2011. Nasri (about £25m) in Aug 2011. Sagna (free) in summer 2014.
- **Titles:** City won the league in 2011/12 (their first in 44 years), 2013/14 and 2017/18 (100 points). Arsenal won no league titles from 2009/10 to 2017/18.
- **Timeline:** UEFA ban on 14 Feb 2020. CAS overturned it on 13 Jul 2020: allegations not established or time-barred, with a fine for non-cooperation. Der Spiegel/Football Leaks in Nov 2018. PL charges on 6 Feb 2023.
- **Deliberately NOT used:** the widely shared 2026 Wenger quote ("legacy is worthless...") has no original source, so it's likely fabricated.

## Footage
- **Wenger soundbites:** HaytersTV, Sky Sports Retro, Guardian Football, The Telegraph, Onlooker/ITN, Total Futbal, BeanymanSports.
- **Others:** Pep (Guardian Football, Jul 2020), Klopp (BeanymanSports, Jul 2020).
- **News:** Sky Sports News (verdict, appeal), ITV News (UEFA ban), Tifo Football (Football Leaks animation).
- **Match and event footage:** Man City (City 4-2 Arsenal 2009, 2018 trophy, 93:20), Arsenal (farewell, touchline), Etihad (2011 announcement).

## Music (credit required in the description)
Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0. Tracks: "Lightless Dawn", "Long Note Four", "Heartbreaking".

## YouTube description draft
On 29 September 2026, an independent commission found that Manchester City used "sham" sponsorship contracts across nine seasons, from 2009/10 to 2017/18, inflating revenues and reducing costs by more than £900 million. Those were Arsène Wenger's last nine seasons at Arsenal.

This video goes back through what Wenger said while it was happening. It covers his 1996 philosophy, losing Adebayor, Touré, Clichy, Nasri and Sagna to City, his July 2011 warning that sponsorship "has to be at the market price", "they have petrol and ideas", and his 2020 reaction to City's UEFA ban. It also covers Pep Guardiola's demand for an apology after the ban was overturned, and where the case stands now. City deny wrongdoing and have appealed, and sanctions have not been decided.

Every video here is researched, written and edited by me. AI is used for narration only.

Music: "Lightless Dawn", "Long Note Four", "Heartbreaking" by Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/
