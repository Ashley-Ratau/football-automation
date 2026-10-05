from __future__ import annotations

import difflib
import json
import os
import re
from pathlib import Path


SIMILARITY_BLOCK_THRESHOLD = 0.72


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def topic_similarity(a: str, b: str) -> float:
    a_norm = normalize_text(a)
    b_norm = normalize_text(b)
    if not a_norm or not b_norm:
        return 0.0
    return difflib.SequenceMatcher(None, a_norm, b_norm).ratio()


def _read_json_topic(candidate: Path) -> list[dict[str, str]]:
    topics: list[dict[str, str]] = []
    if not candidate.exists():
        return topics
    try:
        data = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception:
        return topics
    if "script" in data and isinstance(data["script"], dict):
        script = data["script"]
        topic = script.get("topic") or script.get("research", {}).get("angle")
        if topic:
            topics.append({"source": str(candidate), "topic": str(topic)})
    elif isinstance(data, dict):
        topic = data.get("topic") or data.get("topic_summary")
        if topic:
            topics.append({"source": str(candidate), "topic": str(topic)})
    return topics


def collect_previous_topics(root: Path, memory_path: Path | None = None) -> list[dict[str, str]]:
    topics: list[dict[str, str]] = []
    for project_dir in sorted(root.glob("Political Short *")):
        for candidate in [project_dir / "out" / "build_report.json", project_dir / "script.json"]:
            topics.extend(_read_json_topic(candidate))

    if memory_path and memory_path.exists():
        try:
            text = memory_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        for line in text.splitlines():
            if line.startswith("- Built Political Short") and "topic:" in line:
                topics.append({"source": str(memory_path), "topic": line})

    # de-duplicate by normalized topic while preserving order
    deduped: list[dict[str, str]] = []
    seen = set()
    for item in topics:
        key = normalize_text(item["topic"])
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def reject_duplicate_topic(candidate_topic: str, previous_topics: list[dict[str, str]], threshold: float = SIMILARITY_BLOCK_THRESHOLD) -> None:
    for item in previous_topics:
        if topic_similarity(candidate_topic, item["topic"]) >= threshold:
            raise RuntimeError(f"Refusing duplicate topic because it is too close to prior run history: {item['topic']}")
