cd assets/clips
for round in $(seq 1 120); do
  for f in *.mp4; do
    [ -f "$f" ] || continue; b=${f%.mp4}
    [ -f "$b.words.json" ] && continue; [ -f "$b.fail" ] && continue
    ls "$b"*.part >/dev/null 2>&1 && continue
    ./ffmpeg.exe -y -loglevel error -i "$f" -vn -ac 1 -ar 16000 "$b.wav" && timeout 600 python -u ../../transcribe.py "$b.wav" && mv "$b.words.json" "$b.words.json" 2>/dev/null || touch "$b.fail"
    rm -f "$b.wav"
  done
  [ $(ls *.mp4 2>/dev/null | wc -l) -ge 25 ] && [ $(ls *.words.json 2>/dev/null | wc -l) -ge $(( $(ls *.mp4 | wc -l) - $(ls *.fail 2>/dev/null | wc -l) )) ] && break
  sleep 20
done
echo WATCH_DONE
