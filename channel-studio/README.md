# Football Channel Studio

Local web app for managing the football YouTube channel production workflow.

## Start

Double-click:

`Start Football Channel Studio.bat`

Or run:

```powershell
cd "C:\Users\Wendy\Documents\Football Channel\channel-studio"
npm start
```

Then open:

`http://localhost:4174`

## What It Does Now

- Lists existing video projects in the channel workspace.
- Shows pipeline progress across idea, research, script, clips, voiceover, assets, CapCut, and upload.
- Creates new video folders with starter docs.
- Lets you read and edit production docs locally.
- Lists narrative inserts, b-roll, CapCut workflow files, and upload-package files.
- Opens project folders in Windows Explorer.
- Keeps the workflow CapCut-first.

## Current Guardrail

FIFA-sourced clips are treated as high-risk. Use original graphics, federation/training footage, press clips, or safe b-roll replacements.

## Future Integrations

- OpenAI script assistant and TTS generation from inside the app.
- Clip search/download queue.
- Thumbnail generation queue.
- YouTube API upload and metadata publishing.
- Local status tracking for each task.
