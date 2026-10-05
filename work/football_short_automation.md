# Football Shorts Automation

This workspace now has a full hands-off runner for the football Shorts workflow.

## What it does

1. Finds fresh football news ideas.
2. Rejects topics that look too close to previous videos.
3. Writes the research, script, upload metadata, clip plan, thumbnail plan, and edit brief.
4. Generates voiceover with ElevenLabs at the preferred faster pace.
5. Pulls high-quality portrait images for B-roll.
6. Finds a narrative insert clip when the story needs one.
7. Builds the final vertical video.
8. Uploads the video to YouTube as public.
9. Sets the thumbnail.
10. Records the run so the next pass avoids duplicates.

## Files

- `work/football_short_automation.py` - main runner
- `work/run_football_short_automation.ps1` - launch wrapper with logs
- `work/install_football_short_automation_task.ps1` - schedules the two-hour run

## Notes

- Portrait images are used as the main B-roll.
- Each image stays on screen for 3 seconds or less.
- Voiceover cuts fully around insert clips.
- Captions stay off unless requested.
- The runner avoids duplicate or near-duplicate topics.
