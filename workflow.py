from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from database import add_story_source, get_raw_item, get_story_by_id, get_story_history, get_story_sources, log_story_history, update_story


class PermissionError(Exception):
    pass


def ensure_user_role(user: Optional[dict], expected_roles: List[str]) -> None:
    if user is None:
        raise PermissionError("User session is missing.")
    if user.get("role") not in expected_roles:
        raise PermissionError("You do not have permission to perform this action.")


def can_publish_story(user: Optional[dict], story: Optional[dict]) -> None:
    ensure_user_role(user, ["EDITOR"])
    if story is None:
        raise PermissionError("Story not found.")
    if story.get("status") == "PUBLISHED":
        raise PermissionError("This story has already been published.")


def publish_story(story_id: int, editor_id: int, user: Optional[dict]) -> dict:
    can_publish_story(user, get_story_by_id(story_id))
    story = get_story_by_id(story_id)
    if story is None:
        raise PermissionError("Story not found.")
    if story["status"] == "PUBLISHED":
        raise PermissionError("This story has already been published.")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    update_story(story_id, status="PUBLISHED", published_at=now, editor_id=editor_id)
    log_story_history(story_id, "PUBLISHED", editor_id, "Story published by editor.")
    return get_story_by_id(story_id)


def submit_to_editor(story_id: int, user: Optional[dict]) -> dict:
    ensure_user_role(user, ["REPORTER"])
    story = get_story_by_id(story_id)
    if story is None:
        raise PermissionError("Story not found.")
    if story["status"] == "PUBLISHED":
        raise PermissionError("Cannot resubmit a published story.")
    update_story(story_id, status="IN_REVIEW")
    log_story_history(story_id, "SUBMITTED_TO_EDITOR", user["id"], "Story submitted for editorial review.")
    return get_story_by_id(story_id)


def approve_story(story_id: int, user: Optional[dict]) -> dict:
    ensure_user_role(user, ["EDITOR"])
    story = get_story_by_id(story_id)
    if story is None:
        raise PermissionError("Story not found.")
    update_story(story_id, status="APPROVED")
    log_story_history(story_id, "APPROVED", user["id"], "Story approved by editor.")
    return get_story_by_id(story_id)


def save_story_draft(story_id: int, title: str, summary: str, user: Optional[dict]) -> dict:
    if user is None:
        raise PermissionError("User session is missing.")
    story = get_story_by_id(story_id)
    if story is None:
        raise PermissionError("Story not found.")
    if title.strip() == "" or summary.strip() == "":
        raise PermissionError("Title and summary are required.")
    update_story(story_id, title=title.strip(), summary=summary.strip())
    log_story_history(story_id, "DRAFT_SAVED", user["id"], "Draft updated.")
    return get_story_by_id(story_id)


def merge_story_sources(target_story_id: int, source_story_id: int, user: Optional[dict]) -> dict:
    ensure_user_role(user, ["EDITOR"])
    target_story = get_story_by_id(target_story_id)
    source_story = get_story_by_id(source_story_id)
    if target_story is None or source_story is None:
        raise PermissionError("One or both stories could not be found.")
    if target_story_id == source_story_id:
        raise PermissionError("Cannot merge a story into itself.")
    source_items = get_story_sources(source_story_id)
    for item in source_items:
        add_story_source(target_story_id, item["id"])
    log_story_history(target_story_id, "MERGED_WITH_EXISTING_STORY", user["id"], f"Merged sources from story {source_story_id} after publication.")
    story = get_story_by_id(target_story_id)
    return story


def get_story_with_sources(story_id: int) -> dict:
    story = get_story_by_id(story_id)
    if story is None:
        raise PermissionError("Story not found.")
    story["sources"] = get_story_sources(story_id)
    story["history"] = get_story_history(story_id)
    return story
