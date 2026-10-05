from __future__ import annotations

import json
from pathlib import Path

from googleapiclient.http import MediaFileUpload

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work"))

from youtube_oauth_tool import drive_service  # noqa: E402


PARENT_ID = "194Q_pu5zXVQOHnUVKHfuBPA77xP5gWtg"
REMOVE_FOLDER_NAMES = {
    "06 Rough Preview",
    "07 Source Log",
    "08 Raw Sources - Optional",
}
PDF_PATH = (
    ROOT
    / "Editor Deliveries"
    / "The World Cup Has A SERIOUS Norway Problem - Editor Package"
    / "00 Instructions"
    / "Editor Instructions - Norway Problem.pdf"
)
PDF_NAME = "Editor Instructions - Norway Problem.pdf"


def list_children(service, parent_id: str, name: str | None = None):
    q = [f"'{parent_id}' in parents", "trashed = false"]
    if name:
        safe_name = name.replace("'", "\\'")
        q.append(f"name = '{safe_name}'")
    return (
        service.files()
        .list(
            q=" and ".join(q),
            fields="files(id,name,mimeType,parents,webViewLink)",
            pageSize=100,
            spaces="drive",
        )
        .execute()
        .get("files", [])
    )


def main() -> None:
    service = drive_service()
    removed = []
    for item in list_children(service, PARENT_ID):
        if item["name"] in REMOVE_FOLDER_NAMES:
            service.files().update(fileId=item["id"], body={"trashed": True}).execute()
            removed.append(item)

    instruction_folders = list_children(service, PARENT_ID, "00 Instructions")
    updated_pdf = None
    if instruction_folders and PDF_PATH.exists():
        instruction_id = instruction_folders[0]["id"]
        pdfs = list_children(service, instruction_id, PDF_NAME)
        media = MediaFileUpload(str(PDF_PATH), mimetype="application/pdf", resumable=True)
        if pdfs:
            updated_pdf = (
                service.files()
                .update(
                    fileId=pdfs[0]["id"],
                    media_body=media,
                    fields="id,name,webViewLink,mimeType",
                )
                .execute()
            )
        else:
            updated_pdf = (
                service.files()
                .create(
                    body={"name": PDF_NAME, "parents": [instruction_id]},
                    media_body=media,
                    fields="id,name,webViewLink,mimeType",
                )
                .execute()
            )

    remaining = list_children(service, PARENT_ID)
    result = {
        "removed": [{"id": x["id"], "name": x["name"]} for x in removed],
        "updated_pdf": updated_pdf,
        "remaining_top_level": [x["name"] for x in remaining],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
