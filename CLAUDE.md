# Football Channel automation

This repo mirrors `C:\Users\Wendy\Documents\Football Channel` on the PC, so the same
video workflow runs in Claude Code cloud sessions.

## Layout
- `Videos/<slug>/` holds one folder per video, e.g. `Videos/wenger-warned-us/` ("Arsène Wenger warned us...")
  and `Videos/klopp-was-right/`.
- Inside each video folder:
  - `script.json`: the scene list. `{"type":"vo","name","text"}` is narration;
    `{"type":"quote","name","clip":<YouTube ID>,"from":<first words>,"to":<last words>,"card","fix"}` is a soundbite.
  - `build.py`: plans the shots and renders `final video/<slug>.mp4` (log at `_tmp/build.log`, ends with `Done`).
  - `gfx.py`, `quotes.py`, `produce_audio.py`, `contact.py`: helpers shared across videos.
  - `assets/clips/<id>.mp4` with `<id>.info.json`, `<id>.txt` and `<id>.words.json` (word-level Whisper transcript).
  - `assets/broll/`, `assets/music/`, `assets/fonts/`, `assets/sfx/`.

## The workflow (the "Wenger pipeline")
1. Research the angle, then find source interviews and press conferences on YouTube.
2. Download each clip:
   `python -m yt_dlp -q --no-warnings --extractor-args "youtube:player_client=web_embedded" -f "bv*[height<=1080][vcodec^=avc1]+ba/bv*[height<=1080]+ba/b" --merge-output-format mp4 --write-info-json -o "<id>.%(ext)s" "https://www.youtube.com/watch?v=<id>"`
   (b-roll at 720p to save space).
3. Transcribe with faster-whisper (`WhisperModel('small.en', compute_type='int8')`, `word_timestamps=True`, `vad_filter=True`)
   to `<id>.words.json` and `<id>.txt`. Check quotes against published reports, because Whisper mishears words (e.g. "illegal" vs "legal").
4. Write `script.json`. For a new video, start from `Videos/wenger-warned-us/` by copying `build.py`, the helpers, fonts, sfx and music.
5. Run `python build.py > _tmp/build.log 2>&1` in the background (about 30 minutes), then wait for `Done`.
6. QC: check loudness (`ffmpeg -i F -af ebur128 -f null -` should hit YouTube's target), make a contact sheet
   (`fps=1/4,scale=320:-1,tile=8x14`), and transcribe the final audio to check every line.
7. Write the notes and description file. Thumbnail and upload only after the user approves.

## Cloud vs PC differences
- `scripts/cloud-setup.sh` runs at session start. It installs `requirements.txt` and symlinks
  `assets/clips/ffmpeg.exe` to the system `ffmpeg`, so the PC paths keep working.
- Source footage and renders are git-ignored, so in a fresh cloud session re-download clips from the IDs in `script.json`.
  Transcripts (`*.words.json`, `*.txt`, `*.info.json`) are committed, so you don't need to re-transcribe.
- Cloud sessions are temporary. Commit and push scripts and notes. To keep a finished video, send it to the user, because MP4s are not in git.
- Run `bash scripts/check-cloud.sh` first. It checks tools, network access (YouTube, Hugging Face) and that the repo contents are present.
- API keys (e.g. the voiceover provider used by `produce_audio.py`) come from environment variables set in the cloud environment settings. Never commit them.
