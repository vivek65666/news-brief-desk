from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from database import get_all_stories, get_raw_items, get_story_sources, get_story_history, get_user_by_id
from utils.helpers import parse_iso, to_human_time


def get_published_stories() -> List[dict]:
    stories = []
    for story in get_all_stories():
        if story["status"] != "PUBLISHED":
            continue
        story_dict = dict(story)
        raw_sources = get_story_sources(story["id"])
        earliest_source = min(raw_sources, key=lambda item: item["received_at"], default=None)
        published_at = parse_iso(story["published_at"]) if story.get("published_at") else None
        incoming_at = parse_iso(earliest_source["received_at"]) if earliest_source else published_at
        if published_at and incoming_at:
            delay = (published_at - incoming_at).total_seconds()
            story_dict["time_to_publish_seconds"] = delay
            story_dict["time_to_publish_human"] = to_human_time(delay)
        else:
            story_dict["time_to_publish_seconds"] = 0
            story_dict["time_to_publish_human"] = "0m"
        story_dict["source_count"] = len(raw_sources)
        story_dict["history"] = get_story_history(story["id"])
        story_dict["reporter"] = get_user_by_id(story["reporter_id"])
        story_dict["editor"] = get_user_by_id(story["editor_id"]) if story.get("editor_id") else None
        stories.append(story_dict)
    stories.sort(key=lambda item: item["published_at"] or "", reverse=True)
    return stories


def get_dashboard_metrics() -> dict:
    now = datetime.now(timezone.utc)
    published = get_published_stories()
    raw_items = get_raw_items()
    awaiting_editor = sum(1 for story in get_all_stories() if story["status"] in {"DRAFT", "IN_REVIEW", "APPROVED"})
    today = now.strftime("%Y-%m-%d")
    yesterday = (now.timestamp() - 86400)
    published_today = 0
    published_yesterday = 0
    delays = []
    for story in published:
        published_at = parse_iso(story["published_at"]) if story.get("published_at") else None
        if published_at:
            delays.append(story["time_to_publish_seconds"])
            if published_at.strftime("%Y-%m-%d") == today:
                published_today += 1
            if published_at.strftime("%Y-%m-%d") == datetime.fromtimestamp(yesterday, tz=timezone.utc).strftime("%Y-%m-%d"):
                published_yesterday += 1
    avg_delay = sum(delays) / len(delays) if delays else 0
    return {
        "published_total": len(published),
        "published_yesterday": published_yesterday,
        "published_today": published_today,
        "average_time_to_publish": to_human_time(avg_delay),
        "stories_awaiting_editor": awaiting_editor,
        "incoming_items": len(raw_items),
        "published": published,
    }
