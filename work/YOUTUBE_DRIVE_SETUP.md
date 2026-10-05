# YouTube + Google Drive API Setup

This workspace uses split Google OAuth tokens.

## Connected Services

YouTube:

- Token: `work/secrets/youtube_token_youtube_only.json`
- Scopes:
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube.force-ssl`
  - `https://www.googleapis.com/auth/yt-analytics.readonly`

Drive:

- Token: `work/secrets/youtube_token_drive_only.json`
- Scope:
  - `https://www.googleapis.com/auth/drive.file`

OAuth client:

- `work/secrets/youtube_oauth_client.json`

## Important Rule

Do not use a combined OAuth token for this workflow. YouTube calls should use the YouTube-only token. Drive calls should use the Drive-only token.

## Helper Script

Use:

`work/youtube_oauth_tool.py`

Useful commands:

```powershell
python work/youtube_oauth_tool.py doctor
python work/youtube_oauth_tool.py whoami
python work/youtube_oauth_tool.py auth-youtube
python work/youtube_oauth_tool.py auth-drive
python work/youtube_oauth_tool.py upload --file "path\to\video.mp4" --title "Title" --description "Description" --privacy unlisted --tags tag1 tag2 tag3
python work/youtube_oauth_tool.py thumbnail --video-id VIDEO_ID --file "path\to\thumbnail.png"
python work/youtube_oauth_tool.py drive-create-folder --name "Folder Name"
python work/youtube_oauth_tool.py drive-upload --file "path\to\file.png" --parent-id DRIVE_FOLDER_ID
```

## Upload Convention

For each video project, save:

- Final CapCut export in `final video/capcut export/`
- Final thumbnail in `final video/thumbnail/`
- Upload result notes in `final video/upload records/`

Upload as `unlisted` first, check the YouTube copyright screen, then publish only after the claim status is acceptable.
