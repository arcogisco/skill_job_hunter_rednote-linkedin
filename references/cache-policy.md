# Cache Policy

Avoid repeated retrieval when the same job has already been found.

## Default Storage

If the user provides a save path, use that exact location.

Otherwise:

- when invoked through the OpenClaw API, store normalized results in the OpenClaw memory backend
- if that backend is unavailable, a user-provided save path is required for cross-run dedupe
- if neither exists, deduplicate only within the current run and report that persistence was unavailable

## Minimum Stored Fields

Store:

- source type
- company name
- role title
- city
- keywords
- Xiaohongshu link
- LinkedIn link
- first seen time
- last seen time
- latest summary

## Duplicate Detection Order

1. exact Xiaohongshu link
2. exact LinkedIn link

Do not use text-only fields such as `company + role + city` for persistent dedupe, because they can cause false merges.

## Update Rules

If a cached result already exists:

- update the record when the new result has a clearer title, city, or link
- merge newly found email or refer data only when explicitly stated
- never overwrite a concrete field with a weaker vague value

## Freshness Guidance

Prefer reusing cached results when the same role clearly appears again.
If freshness becomes important, add a time window outside this skill rather than forcing the skill to re-search everything every time.
