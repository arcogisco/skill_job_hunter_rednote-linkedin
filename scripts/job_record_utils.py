#!/usr/bin/env python3
"""
Shared helpers for job-record normalization, deduplication, and caching.
"""

from __future__ import annotations

import re
from typing import Any

EMPTY_VALUES = ("", None, [], {})

COMPANY_ALIASES = {
    "字节": "字节跳动",
    "bytedance": "字节跳动",
    "tiktok": "字节跳动",
    "xiaohongshu": "小红书",
    "rednote": "小红书",
}

CITY_ALIASES = {
    "sf bay area": "san francisco bay area",
    "bay area": "san francisco bay area",
    "nyc": "new york",
}

PREFERRED_LONGER_FIELDS = {"summary", "city", "role_name", "company_name"}


def normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[|,;/]+", " ", value)
    return value.strip()


def normalize_company(value: str) -> str:
    value = normalize_text(value)
    return COMPANY_ALIASES.get(value, value)


def normalize_city(value: str) -> str:
    value = normalize_text(value)
    return CITY_ALIASES.get(value, value)


def normalize_keywords(value: Any) -> list[str]:
    if isinstance(value, str):
        parts = re.split(r"[\/|,;]+", value)
    elif isinstance(value, list):
        parts = [str(item) for item in value]
    else:
        parts = []

    keywords: list[str] = []
    seen: set[str] = set()
    for part in parts:
        cleaned = part.strip()
        token = normalize_text(cleaned)
        if token and token not in seen:
            seen.add(token)
            keywords.append(cleaned)
    return keywords


def normalize_job_record(job: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(job)
    normalized["company_name_normalized"] = normalize_company(str(job.get("company_name", "")))
    normalized["role_name_normalized"] = normalize_text(str(job.get("role_name", "")))
    normalized["city_normalized"] = normalize_city(str(job.get("city", "")))
    normalized["keywords"] = normalize_keywords(job.get("keywords", []))
    normalized["match_key"] = "|".join(
        [
            normalized["company_name_normalized"],
            normalized["role_name_normalized"],
            normalized["city_normalized"],
        ]
    )
    return normalized


def primary_key(job: dict[str, Any]) -> str:
    normalized = normalize_job_record(job)
    xhs = normalize_text(str(normalized.get("xiaohongshu_link", "")))
    if xhs:
        return f"xhs:{xhs}"
    linkedin = normalize_text(str(normalized.get("linkedin_link", "")))
    if linkedin:
        return f"li:{linkedin}"
    return ""


def merge_job_records(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    merged = normalize_job_record(old)
    candidate = normalize_job_record(new)

    for key, value in candidate.items():
        if value in EMPTY_VALUES:
            continue
        current = merged.get(key)
        if current in EMPTY_VALUES:
            merged[key] = value
            continue
        if key == "keywords":
            merged[key] = normalize_keywords(list(current) + list(value))
            continue
        if key in PREFERRED_LONGER_FIELDS and len(str(value)) > len(str(current)):
            merged[key] = value

    return normalize_job_record(merged)
