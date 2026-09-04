from __future__ import annotations

from datetime import datetime
from typing import Iterable, List


def normalize_text(value: str) -> str:
    return " ".join((value or "").lower().replace("-", " ").replace("/", " ").split())


def to_human_time(delta_seconds: float) -> str:
    total_seconds = max(int(delta_seconds), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    if minutes:
        return f"{minutes}m"
    return f"{total_seconds}s"


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def title_case(value: str) -> str:
    return value.replace("-", " ").title()


def unique_by_key(items: Iterable[dict], key: str) -> List[dict]:
    seen = set()
    unique_items = []
    for item in items:
        marker = item.get(key)
        if marker in seen:
            continue
        seen.add(marker)
        unique_items.append(item)
    return unique_items
