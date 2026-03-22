#!/usr/bin/env python3
"""
Append or update normalized jobs in a JSON cache file.

This is a local fallback helper when OpenClaw memory is not the active backend.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from job_record_utils import merge_job_records, normalize_job_record, primary_key


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_cache(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_cache(path: Path, jobs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(jobs, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", required=True, help="Path to a JSON cache file.")
    parser.add_argument("--input", required=True, help="Path to a JSON file containing a list of jobs.")
    args = parser.parse_args()

    cache_path = Path(args.cache)
    with open(args.input, "r", encoding="utf-8") as handle:
        incoming: list[dict[str, Any]] = json.load(handle)

    existing = load_cache(cache_path)
    by_key = {}
    for job in existing:
        normalized = normalize_job_record(job)
        key = primary_key(normalized)
        if key:
            by_key[key] = normalized

    for job in incoming:
        normalized = normalize_job_record(job)
        key = primary_key(normalized)
        if not key:
            continue
        if key in by_key:
            merged = merge_job_records(by_key[key], normalized)
            merged["last_seen_at"] = now_iso()
            by_key[key] = merged
        else:
            item = normalized
            timestamp = now_iso()
            item.setdefault("first_seen_at", timestamp)
            item["last_seen_at"] = timestamp
            by_key[key] = item

    save_cache(
        cache_path,
        sorted(by_key.values(), key=lambda item: item.get("last_seen_at", ""), reverse=True),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
