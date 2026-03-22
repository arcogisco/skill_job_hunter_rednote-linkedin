# Merge And Ranking Rules

Use best-effort matching across Xiaohongshu and LinkedIn.

## Normalize First

Before matching:

- trim whitespace
- lowercase where appropriate
- normalize obvious punctuation differences
- standardize company aliases when unambiguous
- standardize city aliases when unambiguous
- collapse duplicate keywords

Use `scripts/normalize_job.py` when doing this repeatedly.

## Match Keys

Try to match in this order:

1. exact Xiaohongshu link
2. exact LinkedIn link

For persistent dedupe and cache updates, only use exact-link matches.
Do not merge cached records by text-only heuristics such as company, role, or city.

Allow one-to-many matches when a Xiaohongshu clue appears to map to multiple active LinkedIn jobs.

## Keep Single-Source Results

Keep a result even if only one source exists, as long as it still has action value.

Mark the missing source explicitly:

- Xiaohongshu missing -> `未找到`
- LinkedIn missing -> `未找到`

## Ranking Priority

Sort by:

1. both Xiaohongshu link and LinkedIn link present
2. close match on role, track, and city
3. explicit refer or email clue
4. likely freshness
5. better completeness of company, role, and city fields
6. closeness to the user's stated direction

## Tie-Breaking

When two results likely refer to the same role:

- keep the record with the clearer company name
- keep the record with the clearer city
- keep the record with the direct source link
- merge non-conflicting fields from the weaker record into the stronger one

Use `scripts/dedupe_jobs.py` when you already have a JSON list of candidate jobs.
