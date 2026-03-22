#!/usr/bin/env python3
"""
Sync job-search results into a Feishu Bitable.

This is a lightweight, best-effort client for the current project:
- default base name: job_hunter_rednote-linkedin
- default table name: Jobs
- exact-link dedupe only

Required environment variables:
- FEISHU_APP_ID
- FEISHU_APP_SECRET

Optional environment variables:
- FEISHU_BITABLE_APP_TOKEN
- FEISHU_BITABLE_TABLE_ID
- FEISHU_BITABLE_BASE_NAME
- FEISHU_BITABLE_TABLE_NAME
- FEISHU_BITABLE_FOLDER_TOKEN
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from job_record_utils import normalize_job_record, normalize_keywords

API_BASE = "https://open.feishu.cn/open-apis"
DEFAULT_BASE_NAME = "job_hunter_rednote-linkedin"
DEFAULT_TABLE_NAME = "Jobs"
DEFAULT_BITABLE_ORIGIN = "https://my.feishu.cn"
NETWORK_RETRIES = 3
RETRY_SLEEP_SECONDS = 1.0

TEXT = 1
SINGLE_SELECT = 3
MULTI_SELECT = 4


@dataclass
class FieldSpec:
    name: str
    field_type: int
    options: list[str] | None = None


FIELD_SPECS = [
    FieldSpec("公司名称", TEXT),
    FieldSpec("岗位名称", TEXT),
    FieldSpec("一句话概括", TEXT),
    FieldSpec("关键词", MULTI_SELECT),
    FieldSpec("城市", MULTI_SELECT),
    FieldSpec("Refer", SINGLE_SELECT, ["可 refer", "未明确", "无法判断"]),
    FieldSpec("邮箱", TEXT),
    FieldSpec("小红书链接", TEXT),
    FieldSpec("LinkedIn 链接", TEXT),
    FieldSpec("来源", SINGLE_SELECT, ["小红书", "LinkedIn", "小红书+LinkedIn"]),
    FieldSpec("搜索批次ID", TEXT),
]

LINK_FIELD_NAMES = ("小红书链接", "LinkedIn 链接")
REQUIRED_FIELD_NAMES = {spec.name for spec in FIELD_SPECS}
BLANK_ROW_FIELDS = (
    "文本",
    "公司名称",
    "岗位名称",
    "一句话概括",
    "关键词",
    "城市",
    "Refer",
    "邮箱",
    "小红书链接",
    "LinkedIn 链接",
    "来源",
    "搜索批次ID",
)

def split_slash_values(value: Any) -> list[str]:
    if isinstance(value, list):
        parts = [str(item).strip() for item in value]
    else:
        parts = [part.strip() for part in str(value or "").split("/") if part.strip()]

    seen: set[str] = set()
    values: list[str] = []
    for part in parts:
        if part and part not in seen:
            seen.add(part)
            values.append(part)
    return values


def build_bitable_url(app_token: str, table_id: str) -> str:
    origin = os.getenv("FEISHU_BITABLE_ORIGIN", DEFAULT_BITABLE_ORIGIN).rstrip("/")
    return f"{origin}/base/{app_token}?table={table_id}"


def parse_bitable_url(url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(url.strip())
    path_parts = [part for part in parsed.path.split("/") if part]
    app_token = ""
    if "base" in path_parts:
        try:
            app_token = path_parts[path_parts.index("base") + 1]
        except IndexError:
            app_token = ""
    table_id = urllib.parse.parse_qs(parsed.query).get("table", [""])[0].strip()
    return app_token.strip(), table_id


def source_label(job: dict[str, Any]) -> str:
    has_xhs = bool(str(job.get("xiaohongshu_link", "")).strip())
    has_li = bool(str(job.get("linkedin_link", "")).strip())
    if has_xhs and has_li:
        return "小红书+LinkedIn"
    if has_xhs:
        return "小红书"
    return "LinkedIn"


def map_job_to_fields(job: dict[str, Any], batch_id: str) -> dict[str, Any]:
    normalized = normalize_job_record(job)
    if not link_keys_for_job(normalized):
        return {}

    summary = str(
        normalized.get("summary")
        or normalized.get("one_line_summary")
        or normalized.get("一句话概括")
        or ""
    ).strip()
    refer = str(normalized.get("refer") or normalized.get("Refer") or "未明确").strip() or "未明确"
    if refer not in {"可 refer", "未明确", "无法判断"}:
        refer = "未明确"

    return {
        "公司名称": str(normalized.get("company_name", "")).strip(),
        "岗位名称": str(normalized.get("role_name", "")).strip(),
        "一句话概括": summary,
        "关键词": normalize_keywords(normalized.get("keywords", [])),
        "城市": split_slash_values(normalized.get("city", "")),
        "Refer": refer,
        "邮箱": str(normalized.get("email") or normalized.get("邮箱") or "").strip(),
        "小红书链接": str(normalized.get("xiaohongshu_link", "")).strip(),
        "LinkedIn 链接": str(normalized.get("linkedin_link", "")).strip(),
        "来源": source_label(normalized),
        "搜索批次ID": batch_id,
    }


def link_keys_for_job(job: dict[str, Any]) -> list[str]:
    normalized = normalize_job_record(job)
    keys: list[str] = []
    xhs = str(normalized.get("xiaohongshu_link", "")).strip()
    linkedin = str(normalized.get("linkedin_link", "")).strip()
    if xhs:
        keys.append(f"xhs:{xhs}")
    if linkedin:
        keys.append(f"li:{linkedin}")
    return keys


def link_keys_for_fields(fields: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    xhs = str(fields.get("小红书链接") or "").strip()
    linkedin = str(fields.get("LinkedIn 链接") or "").strip()
    if xhs:
        keys.append(f"xhs:{xhs}")
    if linkedin:
        keys.append(f"li:{linkedin}")
    return keys


def has_meaningful_value(value: Any) -> bool:
    if value in ("", None, [], {}):
        return False
    if isinstance(value, list):
        return any(str(item).strip() for item in value)
    return bool(str(value).strip())


def is_blank_record(fields: dict[str, Any]) -> bool:
    return not any(has_meaningful_value(fields.get(name)) for name in BLANK_ROW_FIELDS)


class FeishuClient:
    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = self._get_tenant_access_token()

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{API_BASE}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        data = None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "close",
        }
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        body = ""
        last_error: Exception | None = None
        for attempt in range(1, NETWORK_RETRIES + 1):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = response.read().decode("utf-8")
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Feishu API {method} {path} failed: HTTP {exc.code} {detail}") from exc
            except urllib.error.URLError as exc:
                last_error = exc
                if attempt >= NETWORK_RETRIES:
                    if "EOF occurred in violation of protocol" in str(exc):
                        return self._request_via_curl(method, url, payload, headers)
                    raise RuntimeError(f"Feishu API {method} {path} failed: {exc}") from exc
                time.sleep(RETRY_SLEEP_SECONDS)

        parsed = json.loads(body)
        if parsed.get("code") not in (0, None):
            raise RuntimeError(f"Feishu API {method} {path} returned error: {parsed}")
        return parsed

    def _request_via_curl(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | None,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        command = ["curl", "--http1.1", "--max-time", "30", "-sS", "-X", method, url]
        for key, value in headers.items():
            command.extend(["-H", f"{key}: {value}"])
        if payload is not None:
            command.extend(["-d", json.dumps(payload, ensure_ascii=False)])

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Feishu curl fallback failed for {method} {url}: {result.stderr.strip() or result.stdout.strip()}")

        parsed = json.loads(result.stdout or "{}")
        if parsed.get("code") not in (0, None):
            raise RuntimeError(f"Feishu curl fallback returned error for {method} {url}: {parsed}")
        return parsed

    def _get_tenant_access_token(self) -> str:
        request = urllib.request.Request(
            url=f"{API_BASE}/auth/v3/tenant_access_token/internal",
            data=json.dumps({"app_id": self.app_id, "app_secret": self.app_secret}).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        payload: dict[str, Any] = {}
        for attempt in range(1, NETWORK_RETRIES + 1):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.URLError as exc:
                if attempt >= NETWORK_RETRIES:
                    if "EOF occurred in violation of protocol" in str(exc):
                        payload = self._get_tenant_access_token_via_curl()
                        break
                    raise RuntimeError(f"Failed to obtain Feishu tenant access token: {exc}") from exc
                time.sleep(RETRY_SLEEP_SECONDS)
        token = payload.get("tenant_access_token")
        if not token:
            raise RuntimeError(f"Failed to obtain Feishu tenant access token: {payload}")
        return token

    def _get_tenant_access_token_via_curl(self) -> dict[str, Any]:
        command = [
            "curl",
            "--http1.1",
            "--max-time",
            "30",
            "-sS",
            "-X",
            "POST",
            f"{API_BASE}/auth/v3/tenant_access_token/internal",
            "-H",
            "Content-Type: application/json; charset=utf-8",
            "-d",
            json.dumps({"app_id": self.app_id, "app_secret": self.app_secret}),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to obtain Feishu tenant access token via curl: {result.stderr.strip() or result.stdout.strip()}")
        return json.loads(result.stdout or "{}")

    def list_apps(self) -> list[dict[str, Any]]:
        payload = self._request("GET", "/bitable/v1/apps", params={"page_size": 500})
        return payload.get("data", {}).get("items", [])

    def create_app(self, name: str, folder_token: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if folder_token:
            body["folder_token"] = folder_token
        return self._request("POST", "/bitable/v1/apps", payload=body).get("data", {})

    def list_tables(self, app_token: str) -> list[dict[str, Any]]:
        payload = self._request("GET", f"/bitable/v1/apps/{app_token}/tables", params={"page_size": 500})
        return payload.get("data", {}).get("items", [])

    def create_table(self, app_token: str, name: str) -> dict[str, Any]:
        candidates = [
            {"name": name},
            {"table": {"name": name}},
        ]
        last_error: Exception | None = None
        for body in candidates:
            try:
                return self._request("POST", f"/bitable/v1/apps/{app_token}/tables", payload=body).get("data", {})
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise RuntimeError(f"Failed to create table {name!r}: {last_error}")

    def list_fields(self, app_token: str, table_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            params={"page_size": 500},
        )
        return payload.get("data", {}).get("items", [])

    def create_field(self, app_token: str, table_id: str, spec: FieldSpec) -> dict[str, Any]:
        body: dict[str, Any] = {
            "field_name": spec.name,
            "type": spec.field_type,
        }
        if spec.options:
            body["property"] = {"options": [{"name": option} for option in spec.options]}
        return self._create_field_via_curl(app_token, table_id, body)

    def _create_field_via_curl(self, app_token: str, table_id: str, body: dict[str, Any]) -> dict[str, Any]:
        command = [
            "curl",
            "--http1.1",
            "--max-time",
            "20",
            "-sS",
            "-X",
            "POST",
            f"{API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            "-H",
            f"Authorization: Bearer {self.token}",
            "-H",
            "Content-Type: application/json; charset=utf-8",
            "-d",
            json.dumps(body, ensure_ascii=False),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(
                f"Feishu curl fallback failed creating field {body.get('field_name')!r}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )
        payload = json.loads(result.stdout or "{}")
        code = payload.get("code")
        if code == 1254014:
            return payload.get("data", {})
        if code not in (0, None):
            raise RuntimeError(
                f"Feishu curl fallback returned error creating field {body.get('field_name')!r}: {payload}"
            )
        return payload.get("data", {})

    def list_records(self, app_token: str, table_id: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        page_token = ""
        while True:
            params = {"page_size": 100}
            if page_token:
                params["page_token"] = page_token
            payload = self._request(
                "GET",
                f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
                params=params,
            )
            data = payload.get("data", {})
            records.extend(data.get("items", []))
            if not data.get("has_more"):
                break
            page_token = data.get("page_token", "")
            if not page_token:
                break
        return records

    def batch_create_records(self, app_token: str, table_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            payload={"records": records},
        ).get("data", {})

    def update_record(self, app_token: str, table_id: str, record_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            payload={"fields": fields},
        ).get("data", {})

    def delete_record(self, app_token: str, table_id: str, record_id: str) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
        ).get("data", {})

    def delete_field(self, app_token: str, table_id: str, field_id: str) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}",
        ).get("data", {})

    def update_field(self, app_token: str, table_id: str, field_id: str, spec: FieldSpec) -> dict[str, Any]:
        body: dict[str, Any] = {
            "field_name": spec.name,
            "type": spec.field_type,
        }
        if spec.options:
            body["property"] = {"options": [{"name": option} for option in spec.options]}
        return self._request(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}",
            payload=body,
        ).get("data", {})


def read_jobs(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise RuntimeError("--input must point to a JSON list of jobs")
    return data


def extract_record_fields(record: dict[str, Any]) -> dict[str, Any]:
    return record.get("fields", {}) if isinstance(record, dict) else {}


def resolve_app_token(
    client: FeishuClient,
    preferred_token: str | None,
    base_name: str,
    folder_token: str | None,
) -> tuple[str, dict[str, Any] | None]:
    if preferred_token:
        return preferred_token, None

    try:
        for item in client.list_apps():
            name = str(item.get("name") or item.get("app_name") or "").strip()
            token = str(item.get("app_token") or item.get("token") or "").strip()
            if name == base_name and token:
                return token, None
    except RuntimeError as exc:
        # Some tenants return 404 for app listing even though direct app creation works.
        if "GET /bitable/v1/apps failed: HTTP 404" not in str(exc):
            raise

    created = client.create_app(base_name, folder_token=folder_token)
    token = str(created.get("app", {}).get("app_token") or created.get("app_token") or "").strip()
    if not token:
        raise RuntimeError(f"Failed to resolve app token for base {base_name!r}: {created}")
    return token, created.get("app") or created


def resolve_table_id(
    client: FeishuClient,
    app_token: str,
    preferred_table_id: str | None,
    table_name: str,
    created_app_data: dict[str, Any] | None = None,
) -> tuple[str, bool]:
    if preferred_table_id:
        return preferred_table_id, False

    if created_app_data:
        default_table_id = str(created_app_data.get("default_table_id") or "").strip()
        if default_table_id:
            return default_table_id, True

    for item in client.list_tables(app_token):
        name = str(item.get("name") or item.get("table_name") or "").strip()
        table_id = str(item.get("table_id") or "").strip()
        if name == table_name and table_id:
            return table_id, False

    created = client.create_table(app_token, table_name)
    table_id = str(created.get("table_id") or created.get("table", {}).get("table_id") or "").strip()
    if not table_id:
        raise RuntimeError(f"Failed to resolve table id for table {table_name!r}: {created}")
    return table_id, True


def resolve_actual_table_name(client: Any, app_token: str, table_id: str, fallback: str) -> str:
    if not hasattr(client, "list_tables"):
        return fallback
    try:
        for item in client.list_tables(app_token):
            current_table_id = str(item.get("table_id") or "").strip()
            if current_table_id == table_id:
                return str(item.get("name") or item.get("table_name") or fallback).strip() or fallback
    except Exception:  # noqa: BLE001
        return fallback
    return fallback


def cleanup_new_table_layout(client: FeishuClient, app_token: str, table_id: str) -> None:
    fields = client.list_fields(app_token, table_id)
    primary_field = next((item for item in fields if item.get("is_primary")), None)
    existing_names = {str(item.get("field_name") or item.get("name") or "").strip() for item in fields}

    if primary_field:
        primary_name = str(primary_field.get("field_name") or primary_field.get("name") or "").strip()
        primary_id = str(primary_field.get("field_id") or primary_field.get("id") or "").strip()
        primary_type = int(primary_field.get("type") or TEXT)
        if (
            primary_name not in REQUIRED_FIELD_NAMES
            and "公司名称" not in existing_names
            and primary_id
            and primary_type == TEXT
        ):
            client.update_field(app_token, table_id, primary_id, FieldSpec("公司名称", TEXT))

    fields = client.list_fields(app_token, table_id)
    for item in fields:
        field_id = str(item.get("field_id") or item.get("id") or "").strip()
        field_name = str(item.get("field_name") or item.get("name") or "").strip()
        is_primary = bool(item.get("is_primary"))
        if not field_id or is_primary:
            continue
        if field_name not in REQUIRED_FIELD_NAMES:
            client.delete_field(app_token, table_id, field_id)

    records = client.list_records(app_token, table_id)
    for record in records:
        record_id = str(record.get("record_id") or record.get("id") or "").strip()
        if not record_id:
            continue
        if is_blank_record(extract_record_fields(record)):
            client.delete_record(app_token, table_id, record_id)


def ensure_fields(client: FeishuClient, app_token: str, table_id: str) -> None:
    existing = client.list_fields(app_token, table_id)
    existing_names = {str(item.get("field_name") or item.get("name") or "").strip() for item in existing}

    for spec in FIELD_SPECS:
        if spec.name in existing_names:
            continue
        client.create_field(app_token, table_id, spec)


def build_existing_record_index(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    by_key: dict[str, dict[str, Any]] = {}
    blank_records: list[dict[str, Any]] = []
    for record in records:
        fields = extract_record_fields(record)
        if is_blank_record(fields):
            blank_records.append(record)
            continue
        for key in link_keys_for_fields(fields):
            by_key[key] = record
    return by_key, blank_records


def merge_for_update(existing_fields: dict[str, Any], new_fields: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing_fields)
    for key, value in new_fields.items():
        if value in ("", None, [], {}):
            continue
        current = merged.get(key)
        if current in ("", None, [], {}):
            merged[key] = value
            continue
        if key in {"关键词", "城市"} and isinstance(value, list):
            seen: set[str] = set()
            combined: list[str] = []
            for item in list(current if isinstance(current, list) else []) + value:
                token = str(item).strip()
                if token and token not in seen:
                    seen.add(token)
                    combined.append(token)
            merged[key] = combined
            continue
        if key in {"一句话概括", "岗位名称", "公司名称", "城市"} and len(str(value)) > len(str(current)):
            merged[key] = value
            continue
        if key == "来源":
            if current != value and "小红书+LinkedIn" in {str(current), str(value)}:
                merged[key] = "小红书+LinkedIn"
            elif current != value and {str(current), str(value)} == {"小红书", "LinkedIn"}:
                merged[key] = "小红书+LinkedIn"
        if key == "搜索批次ID" and value:
            merged[key] = value
    return merged


def sync_jobs(
    client: Any,
    jobs: list[dict[str, Any]],
    *,
    base_name: str,
    table_name: str,
    app_token: str | None = None,
    table_id: str | None = None,
    folder_token: str | None = None,
    batch_id: str | None = None,
    ensure_schema: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    resolved_batch_id = batch_id or f"batch-{int(time.time())}"
    resolved_app_token, created_app_data = resolve_app_token(client, app_token, base_name, folder_token)
    resolved_table_id, table_was_created = resolve_table_id(
        client,
        resolved_app_token,
        table_id,
        table_name,
        created_app_data=created_app_data,
    )
    resolved_table_name = resolve_actual_table_name(client, resolved_app_token, resolved_table_id, table_name)

    if ensure_schema and not dry_run:
        if table_was_created:
            cleanup_new_table_layout(client, resolved_app_token, resolved_table_id)
        ensure_fields(client, resolved_app_token, resolved_table_id)
        existing_records = client.list_records(resolved_app_token, resolved_table_id)
    else:
        existing_records = client.list_records(resolved_app_token, resolved_table_id) if hasattr(client, "list_records") else []

    existing_by_key, blank_records = build_existing_record_index(existing_records)
    creates: list[dict[str, Any]] = []
    updates: list[tuple[str, dict[str, Any]]] = []
    skipped = 0
    pending_by_key: dict[str, dict[str, Any]] = {}
    pending_key_sets: dict[str, set[str]] = {}
    pending_aliases: dict[str, str] = {}

    for job in jobs:
        fields = map_job_to_fields(job, batch_id=resolved_batch_id)
        if not fields:
            skipped += 1
            continue
        link_keys = link_keys_for_fields(fields)
        canonical_key = next((pending_aliases[key] for key in link_keys if key in pending_aliases), "")
        if not canonical_key:
            canonical_key = link_keys[0]

        current = pending_by_key.get(canonical_key)
        if current:
            pending_by_key[canonical_key] = merge_for_update(current, fields)
        else:
            pending_by_key[canonical_key] = fields
        key_set = pending_key_sets.setdefault(canonical_key, set())
        key_set.update(link_keys)
        for key in key_set:
            pending_aliases[key] = canonical_key

    blank_record_ids = [
        str(record.get("record_id") or record.get("id") or "").strip()
        for record in blank_records
        if str(record.get("record_id") or record.get("id") or "").strip()
    ]
    blank_index = 0
    created_via_blank_rows = 0

    for canonical_key, fields in pending_by_key.items():
        link_keys = list(pending_key_sets.get(canonical_key, {canonical_key}))
        existing = next((existing_by_key[key] for key in link_keys if key in existing_by_key), None)
        if existing:
            existing_fields = extract_record_fields(existing)
            merged = merge_for_update(existing_fields, fields)
            updates.append((str(existing.get("record_id") or existing.get("id") or ""), merged))
        else:
            if blank_index < len(blank_record_ids):
                updates.append((blank_record_ids[blank_index], fields))
                blank_index += 1
                created_via_blank_rows += 1
            else:
                creates.append({"fields": fields})

    if not dry_run:
        if creates:
            client.batch_create_records(resolved_app_token, resolved_table_id, creates)
        for record_id, fields in updates:
            if record_id:
                client.update_record(resolved_app_token, resolved_table_id, record_id, fields)

    return {
        "app_token": resolved_app_token,
        "table_id": resolved_table_id,
        "bitable_url": build_bitable_url(resolved_app_token, resolved_table_id),
        "base_name": base_name,
        "table_name": resolved_table_name,
        "created": len(creates) + created_via_blank_rows,
        "updated": len(updates) - created_via_blank_rows,
        "skipped": skipped,
        "dry_run": dry_run,
        "batch_id": resolved_batch_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to a JSON file containing a list of jobs.")
    parser.add_argument("--base-name", default=os.getenv("FEISHU_BITABLE_BASE_NAME", DEFAULT_BASE_NAME))
    parser.add_argument("--table-name", default=os.getenv("FEISHU_BITABLE_TABLE_NAME", DEFAULT_TABLE_NAME))
    parser.add_argument("--app-token", default=os.getenv("FEISHU_BITABLE_APP_TOKEN", ""))
    parser.add_argument("--table-id", default=os.getenv("FEISHU_BITABLE_TABLE_ID", ""))
    parser.add_argument("--bitable-url", default=os.getenv("FEISHU_BITABLE_URL", ""))
    parser.add_argument("--folder-token", default=os.getenv("FEISHU_BITABLE_FOLDER_TOKEN", ""))
    parser.add_argument("--batch-id", default="", help="Optional search batch id.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-schema-sync",
        action="store_true",
        help="Skip field auto-create/update for existing tables that do not grant schema edit permission.",
    )
    args = parser.parse_args()

    app_id = os.getenv("FEISHU_APP_ID", "").strip()
    app_secret = os.getenv("FEISHU_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise RuntimeError("FEISHU_APP_ID and FEISHU_APP_SECRET are required.")

    parsed_app_token = ""
    parsed_table_id = ""
    if args.bitable_url:
        parsed_app_token, parsed_table_id = parse_bitable_url(args.bitable_url)

    jobs = read_jobs(args.input)
    client = FeishuClient(app_id, app_secret)
    summary = sync_jobs(
        client,
        jobs,
        base_name=args.base_name,
        table_name=args.table_name,
        app_token=args.app_token or parsed_app_token or None,
        table_id=args.table_id or parsed_table_id or None,
        folder_token=args.folder_token or None,
        batch_id=args.batch_id or None,
        ensure_schema=not args.skip_schema_sync,
        dry_run=args.dry_run,
    )
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
