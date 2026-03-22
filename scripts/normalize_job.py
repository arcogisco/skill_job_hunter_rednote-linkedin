#!/usr/bin/env python3
"""
Normalize job records for matching and caching.

Input:
  JSON object from stdin or --input path

Output:
  normalized JSON object
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from job_record_utils import normalize_job_record


def _read_input(path: str | None) -> dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to a JSON file containing one job object.")
    args = parser.parse_args()

    job = _read_input(args.input)
    json.dump(normalize_job_record(job), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
