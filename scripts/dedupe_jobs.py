#!/usr/bin/env python3
"""
Deduplicate a JSON array of job objects.

Input:
  JSON array from stdin or --input path

Output:
  JSON array with duplicates merged
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from job_record_utils import merge_job_records, normalize_job_record, primary_key


def read_jobs(path: str | None) -> list[dict[str, Any]]:
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to a JSON file containing a list of jobs.")
    args = parser.parse_args()

    jobs = read_jobs(args.input)
    merged: dict[str, dict[str, Any]] = {}
    unique_without_links: list[dict[str, Any]] = []
    for job in jobs:
        normalized = normalize_job_record(job)
        key = primary_key(normalized)
        if not key:
            unique_without_links.append(normalized)
            continue
        if key in merged:
            merged[key] = merge_job_records(merged[key], normalized)
        else:
            merged[key] = normalized

    json.dump(list(merged.values()) + unique_without_links, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
