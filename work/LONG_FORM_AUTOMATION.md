# Long-Form Football Automation

This workspace now has one reusable long-form workflow:

`work/football_long_form_automation.py`

It adapts the uploaded automation guide to the current Football Channel setup.

## Important Current Rules

- Verify live football facts before scripting. Do not trust model memory for scorelines, match numbers, records, or availability.
- Use no more than five or six inserts. Inserts replace narration completely.
- Prefer press conferences, training, federation footage, fan footage, stills, and original graphics.
- Treat official FIFA, UEFA, and Premier League match footage as high Content ID risk.
- Render a clean automated master, then make a separate final-polish export. CapCut or a reproducible local edit is fine; verify the exported file before upload.
- Upload as private by default, unless the user requests another visibility. Review YouTube copyright checks before publishing.
- Use the split YouTube-only OAuth token already configured in `work/secrets/`.

## Workflow

### 1. Check the machine

```powershell
python work/football_long_form_automation.py doctor
```

### 2. Create a project

```powershell
python work/football_long_form_automation.py create `
  --title "Video title here" `
  --folder "Videos/video-title-here"
```

This creates:

- idea brief
- research dossier
- script
- clip map
- sourcing plan
- asset log
- edit brief
- voiceover log
- `long_form_project.json`
- b-roll, VO, thumbnail, QC, final-video, CapCut, and upload folders

### 3. Complete the research gate

In `long_form_project.json`, set each `research_checks` value to `true` only after the claim has been checked against current sources.

Record source URLs in `02 research dossier.md` and `04 clip map.csv`.

### 4. Configure sections

Each section is either:

- `vo`: narration text plus one or more b-roll files and safe seek offsets
- `insert`: a source file with verified start and end times

The build generates one ElevenLabs file per VO section. Existing files are reused.

### 5. Validate before rendering

```powershell
python work/football_long_form_automation.py validate `
  --project "Videos/video-title-here"
```

Validation blocks:

- incomplete fact-check gates
- missing media
- b-roll offsets beyond source duration
- insert windows beyond source duration
- inserts without audio
- AV1 sources
- malformed section types

Warnings cover thumbnail readiness and non-16:9 framing.

### Avatar insertion quality gate

Before using any Google Vids avatar export:

- Listen to the first 3 seconds and reject the clip if it contains test language such as “this is a Google Vids test avatar.”
- Crop the avatar insert slightly inside the 16:9 frame to hide the Veo watermark in the bottom-right corner. Use a small, consistent crop rather than covering it with a graphic.
- Inspect the first and last frame of every avatar insert after cropping.

### 6. Build

```powershell
python work/football_long_form_automation.py build `
  --project "Videos/video-title-here"
```

The build:

1. Generates section-by-section Gemini 3.1 Flash TTS narration with the Orus voice.
2. Applies the saved `1.2x` speed and voice processing.
3. Creates b-roll micro-cuts with full-frame `1920x1080` crop-fill.
4. Inserts the selected clips with their own audio and no narration underneath.
5. Adds the music bed at low volume when present.
6. Verifies video, audio, resolution, and duration.
7. Extracts one QC frame per section to `_tmp/qc/`.
8. Writes `final video/build_report.json`.

Listen to every `assets/vo/*_check2s.wav` file and inspect every `_tmp/qc/*.jpg` before upload.

### 7. Prepare the upload

```powershell
python work/football_long_form_automation.py prepare-upload `
  --project "Videos/video-title-here"
```

This compresses the thumbnail below YouTube's 2MB limit and writes the upload package with the configured visibility.

### 8. Upload only after QC

```powershell
python work/football_long_form_automation.py upload `
  --project "Videos/video-title-here" `
  --confirm-upload
```

The upload uses `upload.privacy` from `long_form_project.json`, restricted to `private` or `unlisted`.
Review YouTube's copyright screen before changing it to public.

## Editorial standard learned from the Raphinha video

Apply this to future Football Channel long-form videos. The Raphinha project's `shot_timeline.json`, `final video/build_report.json`, and `edit/` scripts are concrete references, but their source names, masks, timings, and crop coordinates are project-specific; adapt them rather than copying them unchanged.

- **B-roll is the first priority.** Build a shot-by-shot map against the narration before the final render. For each spoken beat, choose footage or a graphic that shows the player, action, space, pass, or consequence being discussed. Source more distinct clips when coverage is thin. Use short shots for pace, but do not sacrifice relevance for speed.
- **Audit repetition.** Track the source asset and time range used for every shot. Avoid repeating the same clip or near-identical moments across the video; if a repeat is intentional, give it a clear editorial purpose. Watch the complete timeline for repetition, not just individual sections. Vary tactical graphics to match the specific player and passing route being explained; do not recycle one or two generic diagrams throughout.
- **Keep insert clips distinct.** Inserts use their own audio with no narration underneath. Do not mirror, blur, vignette, or caption an insert merely because surrounding B-roll receives those treatments. Check each insert separately.
- **Final visual polish.** Mirror live-action narration B-roll only where wanted; keep tactical diagrams, labels, and arrows readable. The Raphinha `edit/mirror_vignette.py` and `edit/blur_mirrored_broll.py` show how the rendered section timeline was reconciled with shot timing. A subtle vignette is optional. Locate logos and scoreboards in the actual chosen sources and apply a light, feathered, time-limited blur just strong enough that marks are not clearly legible. Avoid large or distracting blur patches, and inspect several affected frames plus clean frames.
- **Captions when requested.** Burn one short line at a time, with a few words per cue, synchronized to narration only. Do not put captions over insert clips. The Raphinha `edit/build_captions.py` is a reference for word timing and excluding insert windows; verify names and football terms manually. Keep source audio unchanged where possible.
- **Thumbnail.** Favor a clear, realistic, high-quality player cutout with a strong in-action emotion. Keep the background simple, the player dominant and centered, and text minimal (often one word behind or above the player). Inspect at mobile size.
- **Final QC and upload.** Review the whole polished export for narration-to-shot match, repeated B-roll, insert boundaries, excessive blur, caption omissions/overlaps, audio continuity, duration, and thumbnail. Point `long_form_project.json` at the actual polished file and chosen thumbnail before `validate` and `prepare-upload`. Upload privately unless the user explicitly requests another visibility; after processing, check Studio's Notices/Claims and visibility before any later publication.

## Source Download Pattern

YouTube downloads may still require the Android player client:

```powershell
yt-dlp --extractor-args "youtube:player_client=android" `
  -f 18 `
  -o "assets/broll/source-name.mp4" `
  "YOUTUBE_URL"
```

If that fails because of a bot check, use another lawful source or a local cached clip. Never let one unavailable source block the entire production.
