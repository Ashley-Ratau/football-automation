#!/usr/bin/env python3
"""
Local YouTube OAuth helper for the Codex workspace.

What it does:
- Runs the initial OAuth login in your browser
- Saves a refresh token locally
- Verifies the connected channel
- Uploads videos
- Updates titles/descriptions/privacy
- Sets custom thumbnails
- Pulls channel analytics

Expected setup:
- Download the OAuth client JSON from Google Cloud Console
- Save it to: work/secrets/youtube_oauth_client.json
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path
from typing import Iterable, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


ROOT = Path(__file__).resolve().parents[1]
SECRETS_DIR = ROOT / "work" / "secrets"
CLIENT_SECRETS_PATH = SECRETS_DIR / "youtube_oauth_client.json"
TOKEN_PATH = SECRETS_DIR / "youtube_token.json"
YOUTUBE_ONLY_TOKEN_PATH = SECRETS_DIR / "youtube_token_youtube_only.json"
DRIVE_ONLY_TOKEN_PATH = SECRETS_DIR / "youtube_token_drive_only.json"

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]

SCOPES = YOUTUBE_SCOPES + DRIVE_SCOPES


def ensure_secrets_dir() -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)


def load_credentials(token_path: Path, scopes: list[str]) -> Optional[Credentials]:
    if not token_path.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_credentials(
    scopes: list[str] | None = None,
    token_path: Path | None = None,
) -> Credentials:
    ensure_secrets_dir()
    scopes = scopes or SCOPES
    token_path = token_path or TOKEN_PATH
    creds = load_credentials(token_path, scopes)
    if creds and creds.valid:
        return creds

    if not CLIENT_SECRETS_PATH.exists():
        raise SystemExit(
            f"Missing OAuth client file: {CLIENT_SECRETS_PATH}\n"
            "Download the OAuth client JSON from Google Cloud Console and save it there.\n"
            "Use a Desktop app client if possible."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_PATH), scopes)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def profile_token_path(profile: str) -> Path:
    if profile == "youtube":
        return YOUTUBE_ONLY_TOKEN_PATH
    if profile == "drive":
        return DRIVE_ONLY_TOKEN_PATH
    return TOKEN_PATH


def profile_scopes(profile: str) -> list[str]:
    if profile == "youtube":
        return YOUTUBE_SCOPES
    if profile == "drive":
        return DRIVE_SCOPES
    return SCOPES


def auth_profile(profile: str) -> Credentials:
    return get_credentials(profile_scopes(profile), profile_token_path(profile))


def youtube_service():
    return build(
        "youtube",
        "v3",
        credentials=auth_profile("youtube"),
        cache_discovery=False,
    )


def analytics_service():
    return build(
        "youtubeAnalytics",
        "v2",
        credentials=auth_profile("youtube"),
        cache_discovery=False,
    )


def drive_service():
    return build("drive", "v3", credentials=auth_profile("drive"), cache_discovery=False)


def print_json(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_auth(_: argparse.Namespace) -> None:
    creds = get_credentials()
    service = build("youtube", "v3", credentials=creds, cache_discovery=False)
    response = (
        service.channels()
        .list(part="snippet,statistics", mine=True, maxResults=1)
        .execute()
    )
    print_json(
        {
            "status": "connected",
            "token_file": str(TOKEN_PATH),
            "scopes": creds.scopes or SCOPES,
            "channel": response.get("items", [{}])[0],
        }
    )


def cmd_auth_youtube(_: argparse.Namespace) -> None:
    creds = auth_profile("youtube")
    service = build("youtube", "v3", credentials=creds, cache_discovery=False)
    response = service.channels().list(part="snippet,statistics", mine=True, maxResults=1).execute()
    print_json(
        {
            "status": "connected",
            "profile": "youtube",
            "token_file": str(YOUTUBE_ONLY_TOKEN_PATH),
            "scopes": creds.scopes or YOUTUBE_SCOPES,
            "channel": response.get("items", [{}])[0],
        }
    )


def cmd_auth_drive(_: argparse.Namespace) -> None:
    creds = auth_profile("drive")
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    response = service.about().get(fields="user,storageQuota").execute()
    print_json(
        {
            "status": "connected",
            "profile": "drive",
            "token_file": str(DRIVE_ONLY_TOKEN_PATH),
            "scopes": creds.scopes or DRIVE_SCOPES,
            "about": response,
        }
    )


def cmd_reset_auth(_: argparse.Namespace) -> None:
    ensure_secrets_dir()
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
        print_json({"status": "deleted", "token_file": str(TOKEN_PATH)})
    else:
        print_json({"status": "not_found", "token_file": str(TOKEN_PATH)})


def cmd_reset_auth_youtube(_: argparse.Namespace) -> None:
    ensure_secrets_dir()
    if YOUTUBE_ONLY_TOKEN_PATH.exists():
        YOUTUBE_ONLY_TOKEN_PATH.unlink()
        print_json({"status": "deleted", "token_file": str(YOUTUBE_ONLY_TOKEN_PATH)})
    else:
        print_json({"status": "not_found", "token_file": str(YOUTUBE_ONLY_TOKEN_PATH)})


def cmd_reset_auth_drive(_: argparse.Namespace) -> None:
    ensure_secrets_dir()
    if DRIVE_ONLY_TOKEN_PATH.exists():
        DRIVE_ONLY_TOKEN_PATH.unlink()
        print_json({"status": "deleted", "token_file": str(DRIVE_ONLY_TOKEN_PATH)})
    else:
        print_json({"status": "not_found", "token_file": str(DRIVE_ONLY_TOKEN_PATH)})


def cmd_doctor(_: argparse.Namespace) -> None:
    ensure_secrets_dir()
    report = {
        "client_file_exists": CLIENT_SECRETS_PATH.exists(),
        "token_file_exists": TOKEN_PATH.exists(),
        "youtube_token_exists": YOUTUBE_ONLY_TOKEN_PATH.exists(),
        "drive_token_exists": DRIVE_ONLY_TOKEN_PATH.exists(),
        "client_file": str(CLIENT_SECRETS_PATH),
        "token_file": str(TOKEN_PATH),
        "youtube_token_file": str(YOUTUBE_ONLY_TOKEN_PATH),
        "drive_token_file": str(DRIVE_ONLY_TOKEN_PATH),
        "scopes": SCOPES,
    }
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            report.update(
                {
                    "token_valid": bool(creds.valid),
                    "token_expired": bool(creds.expired),
                    "has_refresh_token": bool(creds.refresh_token),
                    "stored_scopes": creds.scopes or [],
                }
            )
        except Exception as exc:  # noqa: BLE001
            report["token_error"] = str(exc)
    for label, path, scopes in [
        ("youtube", YOUTUBE_ONLY_TOKEN_PATH, YOUTUBE_SCOPES),
        ("drive", DRIVE_ONLY_TOKEN_PATH, DRIVE_SCOPES),
    ]:
        if path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(path), scopes)
                report[f"{label}_token_valid"] = bool(creds.valid)
                report[f"{label}_token_expired"] = bool(creds.expired)
                report[f"{label}_has_refresh_token"] = bool(creds.refresh_token)
                report[f"{label}_stored_scopes"] = creds.scopes or []
            except Exception as exc:  # noqa: BLE001
                report[f"{label}_token_error"] = str(exc)
    print_json(report)


def cmd_whoami(_: argparse.Namespace) -> None:
    service = youtube_service()
    response = (
        service.channels()
        .list(part="snippet,statistics,contentDetails", mine=True, maxResults=1)
        .execute()
    )
    print_json(response)


def cmd_list_uploads(args: argparse.Namespace) -> None:
    service = youtube_service()
    channel = (
        service.channels()
        .list(part="contentDetails,snippet,statistics", mine=True, maxResults=1)
        .execute()
    )
    items = channel.get("items", [])
    if not items:
        raise SystemExit("No connected channel found.")
    uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    response = (
        service.playlistItems()
        .list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist,
            maxResults=args.max_results,
        )
        .execute()
    )
    print_json(response)


def cmd_search(args: argparse.Namespace) -> None:
    service = youtube_service()
    channel = (
        service.channels()
        .list(part="contentDetails", mine=True, maxResults=1)
        .execute()
    )
    items = channel.get("items", [])
    if not items:
        raise SystemExit("No connected channel found.")
    response = (
        service.search()
        .list(
            part="snippet",
            channelId=items[0]["id"],
            q=args.query,
            maxResults=args.max_results,
            type="video",
            order="date",
        )
        .execute()
    )
    print_json(response)


def cmd_drive_find(args: argparse.Namespace) -> None:
    service = drive_service()
    name_query = args.name.replace("'", "\\'")
    q = [f"name contains '{name_query}'", "trashed = false"]
    if args.parent_id:
        q.append(f"'{args.parent_id}' in parents")
    response = (
        service.files()
        .list(
            q=" and ".join(q),
            fields="files(id,name,mimeType,parents,webViewLink,createdTime,modifiedTime)",
            pageSize=args.max_results,
            orderBy="modifiedTime desc",
            spaces="drive",
        )
        .execute()
    )
    print_json(response)


def cmd_drive_create_folder(args: argparse.Namespace) -> None:
    service = drive_service()
    metadata = {
        "name": args.name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if args.parent_id:
        metadata["parents"] = [args.parent_id]
    response = (
        service.files()
        .create(body=metadata, fields="id,name,webViewLink,parents")
        .execute()
    )
    print_json(response)


def cmd_drive_upload(args: argparse.Namespace) -> None:
    service = drive_service()
    path = Path(args.file)
    metadata = {"name": args.name or path.name}
    if args.parent_id:
        metadata["parents"] = [args.parent_id]
    media = MediaFileUpload(str(path), mimetype=args.mime_type or "application/octet-stream", resumable=True)
    response = (
        service.files()
        .create(
            body=metadata,
            media_body=media,
            fields="id,name,mimeType,webViewLink,parents",
        )
        .execute()
    )
    print_json(response)


def cmd_upload(args: argparse.Namespace) -> None:
    service = youtube_service()
    body = {
        "snippet": {
            "title": args.title,
            "description": args.description or "",
            "tags": args.tags or None,
            "categoryId": args.category or "22",
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    body["snippet"] = {k: v for k, v in body["snippet"].items() if v is not None}
    media = MediaFileUpload(
        str(Path(args.file)),
        chunksize=1024 * 1024 * 8,
        resumable=True,
    )
    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            percent = int(status.progress() * 100)
            print(f"upload progress: {percent}%")
    print_json(response)


def cmd_update(args: argparse.Namespace) -> None:
    service = youtube_service()
    parts = ["snippet", "status"]
    current = service.videos().list(part="snippet,status", id=args.video_id).execute()
    items = current.get("items", [])
    if not items:
        raise SystemExit(f"Video not found: {args.video_id}")

    item = items[0]
    snippet = item.get("snippet", {})
    status = item.get("status", {})

    if args.title is not None:
        snippet["title"] = args.title
    if args.description is not None:
        snippet["description"] = args.description
    if args.tags is not None:
        snippet["tags"] = args.tags
    if args.category is not None:
        snippet["categoryId"] = args.category
    if args.privacy is not None:
        status["privacyStatus"] = args.privacy

    body = {
        "id": args.video_id,
        "snippet": snippet,
        "status": status,
    }
    response = service.videos().update(part=",".join(parts), body=body).execute()
    print_json(response)


def cmd_thumbnail(args: argparse.Namespace) -> None:
    service = youtube_service()
    path = Path(args.file)
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    media = MediaFileUpload(str(path), mimetype=mime_type)
    response = service.thumbnails().set(videoId=args.video_id, media_body=media).execute()
    print_json(response)


def cmd_analytics(args: argparse.Namespace) -> None:
    service = analytics_service()
    metrics = args.metrics or "views,estimatedMinutesWatched,subscribersGained,likes,comments"
    dimensions = ",".join(args.dimensions) if args.dimensions else None
    sort = ",".join(args.sort) if args.sort else None
    response = (
        service.reports()
        .query(
            ids=args.ids,
            startDate=args.start_date,
            endDate=args.end_date,
            metrics=metrics,
            dimensions=dimensions,
            filters=args.filters,
            maxResults=args.max_results,
            sort=sort,
        )
        .execute()
    )
    print_json(response)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="YouTube OAuth helper for the Codex workspace.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("auth", help="Run local OAuth login and verify channel access.")
    p.set_defaults(func=cmd_auth)

    p = sub.add_parser("auth-youtube", help="Run OAuth login with YouTube-only scopes.")
    p.set_defaults(func=cmd_auth_youtube)

    p = sub.add_parser("auth-drive", help="Run OAuth login with Drive-only scopes.")
    p.set_defaults(func=cmd_auth_drive)

    p = sub.add_parser("reset-auth", help="Delete the saved OAuth token so you can re-consent cleanly.")
    p.set_defaults(func=cmd_reset_auth)

    p = sub.add_parser("reset-auth-youtube", help="Delete the saved YouTube-only OAuth token.")
    p.set_defaults(func=cmd_reset_auth_youtube)

    p = sub.add_parser("reset-auth-drive", help="Delete the saved Drive-only OAuth token.")
    p.set_defaults(func=cmd_reset_auth_drive)

    p = sub.add_parser("doctor", help="Print local OAuth setup status and stored token details.")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("whoami", help="Print the connected YouTube channel metadata.")
    p.set_defaults(func=cmd_whoami)

    p = sub.add_parser("list-uploads", help="List uploaded videos from the channel's uploads playlist.")
    p.add_argument("--max-results", type=int, default=10)
    p.set_defaults(func=cmd_list_uploads)

    p = sub.add_parser("search", help="Search the connected channel's videos by title or keyword.")
    p.add_argument("--query", required=True)
    p.add_argument("--max-results", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("upload", help="Upload a video file.")
    p.add_argument("--file", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    p.add_argument("--tags", nargs="*", default=None)
    p.add_argument("--category", default="22")
    p.set_defaults(func=cmd_upload)

    p = sub.add_parser("drive-find", help="Search Drive files by name.")
    p.add_argument("--name", required=True)
    p.add_argument("--parent-id", default=None)
    p.add_argument("--max-results", type=int, default=10)
    p.set_defaults(func=cmd_drive_find)

    p = sub.add_parser("drive-create-folder", help="Create a folder in Drive.")
    p.add_argument("--name", required=True)
    p.add_argument("--parent-id", default=None)
    p.set_defaults(func=cmd_drive_create_folder)

    p = sub.add_parser("drive-upload", help="Upload a file to Drive.")
    p.add_argument("--file", required=True)
    p.add_argument("--name", default=None)
    p.add_argument("--parent-id", default=None)
    p.add_argument("--mime-type", default=None)
    p.set_defaults(func=cmd_drive_upload)

    p = sub.add_parser("update", help="Update a video title/description/tags/privacy.")
    p.add_argument("--video-id", required=True)
    p.add_argument("--title", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--privacy", default=None, choices=["private", "unlisted", "public"])
    p.add_argument("--tags", nargs="*", default=None)
    p.add_argument("--category", default=None)
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("thumbnail", help="Upload a custom thumbnail.")
    p.add_argument("--video-id", required=True)
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_thumbnail)

    p = sub.add_parser("analytics", help="Fetch YouTube Analytics report data.")
    p.add_argument("--ids", default="channel==MINE")
    p.add_argument("--start-date", required=True)
    p.add_argument("--end-date", required=True)
    p.add_argument("--metrics", default=None)
    p.add_argument("--dimensions", nargs="*", default=None)
    p.add_argument("--filters", default=None)
    p.add_argument("--max-results", type=int, default=25)
    p.add_argument("--sort", nargs="*", default=None)
    p.set_defaults(func=cmd_analytics)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
