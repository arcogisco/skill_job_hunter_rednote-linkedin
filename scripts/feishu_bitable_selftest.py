#!/usr/bin/env python3
"""
Local self-test for feishu_bitable.py without real Feishu credentials.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from feishu_bitable import DEFAULT_BASE_NAME, DEFAULT_TABLE_NAME, FIELD_SPECS, sync_jobs


class FakeFeishuClient:
    def __init__(self) -> None:
        self.apps = [{"name": DEFAULT_BASE_NAME, "app_token": "app_demo_token"}]
        self.tables = {"app_demo_token": [{"name": DEFAULT_TABLE_NAME, "table_id": "tbl_demo_jobs"}]}
        self.fields = {"tbl_demo_jobs": [{"field_name": spec.name} for spec in FIELD_SPECS]}
        self.records = {
            "tbl_demo_jobs": [
                {
                    "record_id": "rec_blank_1",
                    "fields": {
                        "文本": "",
                    },
                },
                {
                    "record_id": "rec_blank_2",
                    "fields": {
                        "文本": "",
                    },
                },
                {
                    "record_id": "rec_existing_openai",
                    "fields": {
                        "公司名称": "OpenAI",
                        "岗位名称": "Growth Product Manager",
                        "一句话概括": "旧摘要",
                        "关键词": ["Growth", "AI"],
                        "城市": ["San Francisco"],
                        "Refer": "未明确",
                        "邮箱": "",
                        "小红书链接": "https://www.xiaohongshu.com/explore/example-openai?xsec_token=demo_token&xsec_source=pc_search",
                        "LinkedIn 链接": "",
                        "来源": "小红书",
                        "搜索批次ID": "batch-old",
                    },
                }
            ]
        }
        self.created_records: list[dict[str, Any]] = []
        self.updated_records: list[dict[str, Any]] = []

    def list_apps(self) -> list[dict[str, Any]]:
        return self.apps

    def create_app(self, name: str, folder_token: str | None = None) -> dict[str, Any]:
        return {"app_token": "app_created_token"}

    def list_tables(self, app_token: str) -> list[dict[str, Any]]:
        return self.tables.get(app_token, [])

    def create_table(self, app_token: str, name: str) -> dict[str, Any]:
        return {"table_id": "tbl_created"}

    def list_fields(self, app_token: str, table_id: str) -> list[dict[str, Any]]:
        return self.fields.get(table_id, [])

    def create_field(self, app_token: str, table_id: str, spec: Any) -> dict[str, Any]:
        self.fields.setdefault(table_id, []).append({"field_name": spec.name})
        return {"field_id": f"fld_{spec.name}"}

    def list_records(self, app_token: str, table_id: str) -> list[dict[str, Any]]:
        return self.records.get(table_id, [])

    def batch_create_records(self, app_token: str, table_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        self.created_records.extend(records)
        return {"records": records}

    def update_record(self, app_token: str, table_id: str, record_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        self.updated_records.append({"record_id": record_id, "fields": fields})
        return {"record_id": record_id}


def main() -> int:
    sample_path = Path(__file__).resolve().parent.parent / "references" / "jobs.sample.json"
    jobs = json.loads(sample_path.read_text(encoding="utf-8"))
    client = FakeFeishuClient()

    summary = sync_jobs(
        client,
        jobs,
        base_name=DEFAULT_BASE_NAME,
        table_name=DEFAULT_TABLE_NAME,
        batch_id="batch-selftest",
        ensure_schema=True,
        dry_run=False,
    )

    assert summary["created"] == 1, summary
    assert summary["updated"] == 1, summary
    assert summary["skipped"] == 1, summary
    assert len(client.created_records) == 0, client.created_records
    assert len(client.updated_records) == 2, client.updated_records

    created_fields = next(item["fields"] for item in client.updated_records if item["record_id"] == "rec_blank_1")
    updated_fields = next(item["fields"] for item in client.updated_records if item["record_id"] == "rec_existing_openai")

    assert created_fields["公司名称"] == "Anthropic"
    assert created_fields["关键词"] == ["AI Agent", "LLM", "Developer Product"]
    assert created_fields["城市"] == ["San Francisco", "Remote"]

    assert updated_fields["来源"] == "小红书+LinkedIn"
    assert updated_fields["LinkedIn 链接"] == "https://www.linkedin.com/jobs/view/example-openai-1"
    assert updated_fields["邮箱"] == "jobs@example.com"
    assert updated_fields["关键词"] == ["Growth", "AI", "Monetization", "B2B SaaS"]
    assert updated_fields["城市"] == ["San Francisco", "Remote"]

    print(json.dumps({"status": "ok", **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
