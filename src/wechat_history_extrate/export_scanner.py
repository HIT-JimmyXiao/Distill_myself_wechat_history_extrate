from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _safe_load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _message_count(payload: Any) -> int | None:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("messages", "items", "rows", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
        count = payload.get("count")
        if isinstance(count, int):
            return count
    return None


def _scan_bucket(export_root: Path, bucket: str, subdir: str) -> list[dict[str, Any]]:
    folder = export_root / subdir
    if not folder.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(folder.rglob("*.json")):
        payload = _safe_load_json(path)
        records.append(
            {
                "bucket": bucket,
                "source_name": path.stem,
                "relative_path": path.relative_to(export_root).as_posix(),
                "file_size_bytes": path.stat().st_size,
                "message_count": _message_count(payload),
            }
        )
    return records


def scan_export_root(export_root: Path) -> dict[str, Any]:
    export_root = export_root.resolve()
    if not export_root.exists():
        raise FileNotFoundError(f"export root not found: {export_root}")
    private_records = _scan_bucket(export_root, "private", "contacts")
    group_records = _scan_bucket(export_root, "group_reference", "groups")
    return {
        "scanned_at": now_iso(),
        "export_root": str(export_root),
        "private_contact_count": len(private_records),
        "group_count": len(group_records),
        "records": private_records + group_records,
    }

