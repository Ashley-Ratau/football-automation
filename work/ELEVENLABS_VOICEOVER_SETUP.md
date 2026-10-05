# ElevenLabs Voiceover Setup

ElevenLabs is the default voiceover provider going forward. OpenAI TTS can stay as a fallback.

## Secrets

Create this file:

`work/secrets/.env.local`

Add:

```text
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_preferred_voice_id_here
```

Do not paste the API key into production docs or upload logs.

## Check Setup

```powershell
python work/generate_elevenlabs_voiceover.py check-env
```

## List Voices

```powershell
python work/generate_elevenlabs_voiceover.py voices
```

Use this to find the exact `voice_id` for the voice we want.

## Generate Voiceover

```powershell
python work/generate_elevenlabs_voiceover.py generate --project "Video 001 - Norway Problem"
```

Optional:

```powershell
python work/generate_elevenlabs_voiceover.py generate --project "Video 001 - Norway Problem" --voice-id "VOICE_ID"
```

## Output

The script saves:

- `assets/voiceover/elevenlabs/voiceover_narration_clean.txt`
- `assets/voiceover/elevenlabs/elevenlabs_part_01.mp3`
- `assets/voiceover/elevenlabs/voiceover_elevenlabs_full.mp3`

It also appends an ElevenLabs section to:

- `08 voiceover log.md`

## Default Voice Direction

Use a serious, confident, documentary-style football narrator voice:

- controlled drama
- sharp pacing
- natural authority
- not a hype announcer
- clear pronunciation of player and country names

## Current Default Settings

- Voice ID: set in `ELEVENLABS_VOICE_ID`
- Preferred voice ID as of latest test: `wBXNqKUATyqu0RtYt25i`
- Model: `eleven_v3`
- Output format: `mp3_44100_128`

## API Notes

The script uses the ElevenLabs text-to-speech endpoint:

`POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

It passes:

- `xi-api-key`
- `model_id`
- `voice_settings`
- `output_format=mp3_44100_128`
