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
# YouTube changes often; the newest (pre-release) yt-dlp keeps up best.
pip install -q -U --pre --disable-pip-version-check --root-user-action=ignore "yt-dlp[default]" 2>&1 | grep -v -i "warning" || true

# yt-dlp defaults for the cloud: Node solves YouTube's player challenge, and cloud IPs
# need a signed-in session, so use cookies from the YOUTUBE_COOKIES env var (Netscape cookies.txt text).
mkdir -p ~/.config/yt-dlp
{
  echo "--js-runtimes node"
  echo "--remote-components ejs:github"
  if [ -n "${YOUTUBE_COOKIES:-}" ]; then
    # Accept the cookies.txt text as-is, or base64-encoded on one line.
    if printf '%s' "$YOUTUBE_COOKIES" | grep -q 'youtube.com'; then
      printf '%s\n' "$YOUTUBE_COOKIES" > ~/.config/yt-dlp/cookies.txt
    else
      printf '%s' "$YOUTUBE_COOKIES" | tr -d ' \r\n' | base64 -d > ~/.config/yt-dlp/cookies.txt 2>/dev/null || echo "WARN: YOUTUBE_COOKIES is neither cookies.txt text nor base64"
    fi
    # Some settings boxes turn tabs into spaces; cookies.txt needs tabs between its 7 fields.
    sed -i -E '/^(#|$)/! s/ +/\t/g' ~/.config/yt-dlp/cookies.txt
    chmod 600 ~/.config/yt-dlp/cookies.txt
    echo "--cookies $HOME/.config/yt-dlp/cookies.txt"
  fi
} > ~/.config/yt-dlp/config

# The PC scripts call assets/clips/ffmpeg.exe; on Linux point that at the system ffmpeg.
if [ -d Videos ]; then
  find Videos -path '*/assets/clips' -type d | while read -r d; do
    [ -e "$d/ffmpeg.exe" ] || ln -sf "$(command -v ffmpeg)" "$d/ffmpeg.exe"
    [ -e "$d/ffprobe.exe" ] || ln -sf "$(command -v ffprobe)" "$d/ffprobe.exe"
  done
fi

echo "Football pipeline ready: $(ffmpeg -version | head -1 | cut -d' ' -f1-3), yt-dlp $(python3 -m yt_dlp --version)"
