#!/bin/bash
# Preflight: checks that a cloud session can run the whole video pipeline.
# Usage: bash scripts/check-cloud.sh
ok() { echo "  OK   $1"; }
bad() { echo "  FAIL $1"; FAILED=1; }
FAILED=0

echo "Tools"
command -v ffmpeg >/dev/null && ok "ffmpeg" || bad "ffmpeg missing (run scripts/cloud-setup.sh)"
python3 -c "import yt_dlp" 2>/dev/null && ok "yt-dlp" || bad "yt-dlp missing"
python3 -c "import faster_whisper" 2>/dev/null && ok "faster-whisper" || bad "faster-whisper missing"
python3 -c "import PIL" 2>/dev/null && ok "Pillow" || bad "Pillow missing"

echo "Network (environment settings > Network access must allow these)"
for h in www.youtube.com youtubei.googleapis.com i.ytimg.com huggingface.co api.elevenlabs.io; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://$h/" || true)
  [ "$code" != "000" ] && [ "$code" != "403" ] && ok "$h ($code)" || bad "$h blocked"
done
echo "  INFO *.googlevideo.com (YouTube video files) is checked by the test download below"

echo "Secrets"
[ -n "${ELEVENLABS_API_KEY:-}" ] && ok "ELEVENLABS_API_KEY set" || bad "ELEVENLABS_API_KEY not set (add it in the environment settings)"

echo "Repo contents"
[ -d Videos/wenger-warned-us ] && ok "Videos/wenger-warned-us present" || bad "Videos/wenger-warned-us not pushed yet"
[ -f Videos/wenger-warned-us/build.py ] && ok "wenger build.py" || bad "wenger build.py missing"
ls Videos/wenger-warned-us/assets/music/*.mp3 >/dev/null 2>&1 && ok "music tracks" || bad "assets/music/*.mp3 missing (git-ignored; see CLAUDE.md)"

if [ "$FAILED" = 0 ]; then
  echo "Test download (15s of a clip)"
  tmp=$(mktemp -d)
  python3 -m yt_dlp -q --no-warnings --extractor-args "youtube:player_client=web_embedded" \
    -f "b[height<=360]/b" --download-sections "*0-15" -o "$tmp/t.%(ext)s" \
    "https://www.youtube.com/watch?v=62zh2Vb5AZg" && ok "YouTube download" || bad "YouTube download failed"
  rm -rf "$tmp"
fi

[ "$FAILED" = 0 ] && echo "All good: the pipeline can run here." || echo "Some checks failed — see above."
exit $FAILED
