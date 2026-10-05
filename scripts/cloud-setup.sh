#!/bin/bash
# Installs the football channel video pipeline's tools in a Claude Code cloud session.
# Runs automatically at session start (see .claude/settings.json). Safe to re-run.
set -euo pipefail

# Only install in cloud sessions; on the Windows PC everything is already set up.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}"

# ffmpeg (with drawtext / ebur128 / subtitles) — preinstalled on the cloud image, install if missing.
if ! command -v ffmpeg >/dev/null 2>&1; then
  (apt-get update -qq && apt-get install -y -qq ffmpeg fonts-dejavu-core) >/dev/null 2>&1 || echo "WARN: could not install ffmpeg"
fi

# Python packages the pipeline uses: yt-dlp (clips), faster-whisper (transcripts), Pillow (graphics).
pip install -q --disable-pip-version-check --root-user-action=ignore -r requirements.txt 2>&1 | grep -v -i "warning" || true

# The PC scripts call assets/clips/ffmpeg.exe; on Linux point that at the system ffmpeg.
if [ -d Videos ]; then
  find Videos -path '*/assets/clips' -type d | while read -r d; do
    [ -e "$d/ffmpeg.exe" ] || ln -sf "$(command -v ffmpeg)" "$d/ffmpeg.exe"
    [ -e "$d/ffprobe.exe" ] || ln -sf "$(command -v ffprobe)" "$d/ffprobe.exe"
  done
fi

echo "Football pipeline ready: $(ffmpeg -version | head -1 | cut -d' ' -f1-3), yt-dlp $(python3 -m yt_dlp --version)"
