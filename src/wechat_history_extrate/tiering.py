from __future__ import annotations

import math
from datetime import datetime
from typing import Any


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _score_components(contact: dict[str, Any]) -> dict[str, float]:
    message_count = max(int(contact.get("message_count", 0) or 0), 0)
    active_days = max(int(contact.get("active_days", 0) or 0), 0)
    relation_strength = clamp(float(contact.get("relation_strength", 0.0) or 0.0), 0.0, 1.0)
    volume_score = min(math.log1p(message_count) / math.log1p(5000), 1.0)
    activity_score = min(active_days, 180) / 180.0
    return {
        "volume_score": round(volume_score, 4),
        "activity_score": round(activity_score, 4),
        "relation_score": round(relation_strength, 4),
    }


def _assign_tier(score: float) -> str:
    if score >= 0.80:
        return "S"
    if score >= 0.62:
        return "A"
    if score >= 0.42:
        return "B"
    return "Reference"


def tier_contacts(payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    contacts = payload if isinstance(payload, list) else payload.get("contacts", [])
    if not isinstance(contacts, list):
        raise ValueError("contacts payload must be a list or an object with a contacts list")
    tier_counts = {"S": 0, "A": 0, "B": 0, "Reference": 0}
    scored_contacts: list[dict[str, Any]] = []
    for raw_contact in contacts:
        if not isinstance(raw_contact, dict):
            continue
        contact = dict(raw_contact)
        parts = _score_components(contact)
        score = round(
            0.50 * parts["volume_score"] + 0.30 * parts["activity_score"] + 0.20 * parts["relation_score"],
            4,
        )
        tier = _assign_tier(score)
        contact["score_breakdown"] = parts
        contact["score"] = score
        contact["tier"] = tier
        tier_counts[tier] += 1
        scored_contacts.append(contact)
    scored_contacts.sort(key=lambda item: (-float(item["score"]), str(item.get("public_contact_id", ""))))
    return {
        "scored_at": now_iso(),
        "tier_counts": tier_counts,
        "contacts": scored_contacts,
    }

