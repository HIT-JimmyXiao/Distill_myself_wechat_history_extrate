from __future__ import annotations

import hashlib
import re
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d -]{6,}\d)(?!\d)")
WXID_RE = re.compile(r"wxid_[A-Za-z0-9_]+", re.IGNORECASE)
PII_KEYS = {
    "name",
    "nickname",
    "remark",
    "real_name",
    "wxid",
    "contact_id",
    "phone",
    "mobile",
    "email",
    "account",
}


def short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]


def redact_text(text: str) -> str:
    text = EMAIL_RE.sub("[email]", text)
    text = PHONE_RE.sub("[phone]", text)
    text = WXID_RE.sub("[wxid]", text)
    return text


def _public_contact_id(bucket: str, seed: str) -> str:
    prefix = "grp" if bucket == "group_reference" else "pvt"
    return f"{prefix}_{short_hash(seed)}"


def _redact_record(record: dict[str, Any]) -> dict[str, Any]:
    bucket = str(record.get("bucket", "private"))
    seed = str(
        record.get("source_name")
        or record.get("relative_path")
        or record.get("wxid")
        or record.get("contact_id")
        or ""
    )
    public_id = _public_contact_id(bucket, seed or bucket)
    redacted: dict[str, Any] = {
        "bucket": bucket,
        "public_contact_id": public_id,
    }
    for key, value in record.items():
        lower = key.lower()
        if lower in {"source_name", "relative_path", "wxid", "contact_id"}:
            continue
        if lower in PII_KEYS:
            redacted[key] = f"[redacted:{short_hash(str(value))}]" if value else ""
            continue
        if isinstance(value, str):
            redacted[key] = redact_text(value)
        elif isinstance(value, list):
            redacted[key] = [redact_text(item) if isinstance(item, str) else item for item in value]
        else:
            redacted[key] = value
    redacted["public_relative_path"] = f"{'groups' if bucket == 'group_reference' else 'contacts'}/{public_id}.json"
    return redacted


def redact_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError("manifest.records must be a list")
    return {
        "scanned_at": payload.get("scanned_at", ""),
        "private_contact_count": payload.get("private_contact_count", 0),
        "group_count": payload.get("group_count", 0),
        "records": [_redact_record(record) for record in records if isinstance(record, dict)],
    }

