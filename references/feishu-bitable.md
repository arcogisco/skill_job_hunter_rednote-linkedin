# Feishu Bitable Sync

This project includes a lightweight Feishu Bitable sync script:

- [feishu_bitable.py](../scripts/feishu_bitable.py)

## What It Does

- uses Feishu OpenAPI directly
- currently works best with an existing Bitable target
- defaults to base `job_hunter_rednote-linkedin`
- defaults to table `Jobs`
- reuses the same exact-link dedupe rule as the main skill
- creates or updates records in Bitable
- returns the Feishu Bitable link after reuse or creation

## Required Environment Variables

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

## Optional Environment Variables

- `FEISHU_BITABLE_URL`
- `FEISHU_BITABLE_APP_TOKEN`
- `FEISHU_BITABLE_TABLE_ID`
- `FEISHU_BITABLE_BASE_NAME`
- `FEISHU_BITABLE_TABLE_NAME`
- `FEISHU_BITABLE_FOLDER_TOKEN`

If `FEISHU_BITABLE_URL` is available, the script can parse it directly into `app_token` and `table_id`.

If `FEISHU_BITABLE_APP_TOKEN` and `FEISHU_BITABLE_TABLE_ID` are already available, the script uses them directly.
That is the preferred path for the current version.

If they are missing, the script can still try to resolve the default base and table by name, and create them when needed.
Treat that as a secondary path for now.

## Input

The script expects a JSON list of jobs.

Example:

```bash
python3 scripts/feishu_bitable.py --input jobs.json
```

Optional:

```bash
python3 scripts/feishu_bitable.py --input jobs.json --batch-id search-2026-03-22
```

Dry run:

```bash
python3 scripts/feishu_bitable.py --input jobs.json --dry-run
```

## Current Scope

This is intentionally minimal:

- it is tuned first for the case where a Feishu Bitable already exists
- it has been verified for both reusing an existing table and creating a new table inside an existing base
- on a fresh base, it now tries to reuse Feishu's default table instead of always creating a second table
- it only supports the current `Jobs` table schema
- it only deduplicates by exact Xiaohongshu or LinkedIn link
- it skips records that do not have a reliable link
- it can auto-fill Feishu's default blank placeholder rows before appending new ones

## Note

This script is implemented as a best-effort lightweight Feishu client.
It has been syntax-checked and live-tested against a real Feishu tenant for:

- reusing an existing table
- creating a new table inside an existing base

Direct base creation has also been verified, but the full no-existing-Bitable end-to-end path still needs more hardening before it should be treated as the default path.
For that path, the current implementation reuses the default table created by Feishu, cleans default blank rows/irrelevant default columns, and then applies the project schema.

One more tenant-specific note:

- some tenants return `404` for `GET /bitable/v1/apps`
- direct `create_app` can still work in the same tenant
