from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd
import streamlit as st

from ai_service import generate_brief_from_sources
from clustering import build_suggested_groups
from dashboard import get_dashboard_metrics
from database import (
    get_all_stories,
    get_all_users,
    get_raw_items,
    get_story_by_id,
    get_story_history,
    get_story_sources,
    get_user_by_id,
    get_user_by_role,
    init_db,
    insert_story,
    log_story_history,
    update_story,
    add_story_source,
)
from workflow import PermissionError, approve_story, merge_story_sources, publish_story, save_story_draft, submit_to_editor

st.set_page_config(page_title="News Brief Desk", page_icon="📰", layout="wide")


@st.cache_resource

def initialize_app() -> None:
    init_db()


initialize_app()


ROLE_ORDER = ["REPORTER", "EDITOR", "DESK_HEAD"]
USER_OPTIONS = {
    "REPORTER": "Asha Menon",
    "EDITOR": "Rahul Sharma",
    "DESK_HEAD": "Meera Iyer",
}


def app_title() -> str:
    return "Demo Data — Synthetic Newsroom Dataset"


def get_active_user() -> Optional[dict]:
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = 1
    user_id = st.session_state.selected_user
    if user_id is None:
        return None
    return get_user_by_id(user_id)


def nav_label(role: str) -> str:
    labels = {
        "REPORTER": "Reporter",
        "EDITOR": "Editor",
        "DESK_HEAD": "Desk Head",
    }
    return labels.get(role, role)


def render_metric_card(title: str, value: str, subtext: str = "") -> None:
    st.markdown(
        f"""
        <div style="padding: 1rem; border-radius: 12px; background: #f5f7fa; border: 1px solid #dfe6ee; margin-bottom: 0.5rem;">
            <div style="font-size: 0.8rem; color: #596978;">{title}</div>
            <div style="font-size: 1.75rem; font-weight: 700; margin-top: 0.4rem;">{value}</div>
            <div style="font-size: 0.8rem; color: #66788a; margin-top: 0.2rem;">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_story_card(story: dict, role: str) -> None:
    status = story.get("status", "DRAFT")
    st.markdown(f"### {story.get('title', 'Untitled story')}")
    st.caption(f"Status: {status} | Updated: {story.get('updated_at','-')}")
    st.write(story.get("summary", ""))
    source_count = get_story_sources(story["id"])
    if source_count:
        with st.expander(f"Sources ({len(source_count)})"):
            for item in source_count:
                st.markdown(f"- {item['source_name']} — {item['headline']}")
    st.write("")


def show_home() -> None:
    user = get_active_user()
    if user is None:
        st.warning("Select a demo user to continue.")
        return
    metrics = get_dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Published today", str(metrics["published_today"]), "Recent output")
    with col2:
        render_metric_card("Published yesterday", str(metrics["published_yesterday"]), "Prior day")
    with col3:
        render_metric_card("Avg. time to publish", metrics["average_time_to_publish"], "From first source")
    with col4:
        render_metric_card("Incoming items", str(metrics["incoming_items"]), "Open feed")
    st.markdown("### Recent published stories")
    published = metrics["published"][:5]
    if not published:
        st.info("No stories have been published yet.")
    else:
        for story in published:
            with st.container():
                st.markdown(f"**{story['title']}**")
                st.caption(f"Published {story.get('published_at')} — {story.get('time_to_publish_human', '0m')} from first source")
                st.write(story["summary"])
                st.write("---")


def show_incoming() -> None:
    user = get_active_user()
    items = get_raw_items()
    st.markdown("### Incoming items")
    for item in items:
        with st.container():
            st.markdown(f"**{item['headline']}**")
            st.caption(f"{item['source_name']} • {item['source_type']} • {item['received_at']}")
            st.write(item["content"])
            st.write("---")


def show_story_groups() -> None:
    user = get_active_user()
    items = get_raw_items()
    groups = build_suggested_groups(items)
    st.markdown("### Suggested story groups")
    if not groups:
        st.info("No groups found.")
        return
    for idx, group in enumerate(groups, start=1):
        with st.expander(f"Group {idx} — {group['reason']} ({len(group['items'])} items)"):
            if user and user["role"] == "REPORTER":
                if st.button(f"Create story from group {idx}", key=f"story_group_{idx}"):
                    selected_ids = [item["id"] for item in group["items"]]
                    if not selected_ids:
                        st.warning("No items selected.")
                    else:
                        title_base = group["items"][0]["headline"]
                        title = title_base[:80]
                        summary = "".join(f"{item['source_name']}: {item['headline']}\n" for item in group["items"])
                        story_id = insert_story(title, summary, user["id"], status="DRAFT")
                        for raw_id in selected_ids:
                            add_story_source(story_id, raw_id)
                        log_story_history(story_id, "GROUP_CREATED", user["id"], f"Created from grouped raw items {selected_ids}")
                        st.success(f"Story created with ID {story_id}.")
                        st.rerun()
            for item in group["items"]:
                st.markdown(f"- {item['source_name']} — {item['headline']}")


def render_story_drafts() -> None:
    user = get_active_user()
    stories = get_all_stories()
    if not stories:
        st.info("No drafts exist yet.")
        return
    for story in stories:
        if story["status"] == "PUBLISHED":
            continue
        with st.expander(f"{story['title']} ({story['status']})"):
            st.caption(f"Brief source: {story.get('brief_source', 'fallback').upper()}")
            st.write(story["summary"])
            sources = get_story_sources(story["id"])
            if sources:
                st.markdown("**Sources**")
                for item in sources:
                    st.markdown(f"- {item['source_name']} — {item['headline']}")
            if user and user["role"] == "REPORTER":
                if story["status"] in {"DRAFT", "IN_REVIEW"}:
                    if st.button(f"Submit to editor: {story['id']}", key=f"submit_story_{story['id']}"):
                        try:
                            submit_to_editor(story["id"], user)
                            st.success("Story submitted to editor.")
                            st.rerun()
                        except PermissionError as exc:
                            st.error(str(exc))


def show_drafts() -> None:
    user = get_active_user()
    st.markdown("### Draft stories")
    if user is None:
        st.warning("Select a user.")
        return
    if user["role"] == "REPORTER":
        render_story_drafts()
    else:
        st.info("Editor and Desk Head can review stories from Editor Review.")


def show_editor_review() -> None:
    user = get_active_user()
    stories = get_all_stories()
    filtered = [story for story in stories if story["status"] in {"DRAFT", "IN_REVIEW", "APPROVED"}]
    if not filtered:
        st.info("There are no stories awaiting review.")
        return
    for story in filtered:
        with st.container():
            st.markdown(f"### {story['title']} — {story['status']}")
            st.caption(f"Brief generation method: {story.get('brief_source', 'fallback').upper()}")
            summary = story["summary"]
            editor_summary = st.text_area(f"Brief for story {story['id']}", value=summary, key=f"edit_sum_{story['id']}")
            new_title = st.text_input(f"Headline {story['id']}", value=story["title"], key=f"edit_title_{story['id']}")
            sources = get_story_sources(story["id"])
            if sources:
                with st.expander("Source list"):
                    for item in sources:
                        st.markdown(f"- {item['source_name']} — {item['headline']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Save draft", key=f"save_draft_{story['id']}"):
                    if user is None:
                        st.error("Select a user first.")
                    else:
                        try:
                            save_story_draft(story["id"], new_title, editor_summary, user)
                            st.success("Draft updated.")
                        except PermissionError as exc:
                            st.error(str(exc))
            with col2:
                if st.button("Approve", key=f"approve_{story['id']}"):
                    if user is None:
                        st.error("Select a user first.")
                    else:
                        try:
                            approve_story(story["id"], user)
                            st.success("Story approved.")
                            st.rerun()
                        except PermissionError as exc:
                            st.error(str(exc))
            with col3:
                if st.button("Publish", key=f"publish_{story['id']}"):
                    if user is None:
                        st.error("Select a user first.")
                    else:
                        try:
                            story_after = publish_story(story["id"], user["id"], user)
                            st.success(f"Published: {story_after['title']}")
                            st.rerun()
                        except PermissionError as exc:
                            st.error(str(exc))
            st.write("---")


def show_published() -> None:
    stories = [story for story in get_all_stories() if story["status"] == "PUBLISHED"]
    if not stories:
        st.info("No published stories yet.")
        return
    for story in stories:
        with st.expander(f"{story['title']} — Published {story.get('published_at', '')}"):
            st.write(story["summary"])
            st.markdown("**History**")
            for entry in get_story_history(story["id"]):
                st.caption(f"{entry['action']} @ {entry['timestamp']} — {entry.get('details','')}")
            if st.button(f"Merge with another published story {story['id']}", key=f"merge_{story['id']}"):
                target = st.selectbox("Choose another story to merge into this one", [s for s in get_all_stories() if s["id"] != story["id"]], format_func=lambda s: s["title"], key=f"merge_select_{story['id']}")
                if target:
                    try:
                        merge_story_sources(story["id"], target["id"], get_active_user())
                        st.success("Story merged and history recorded.")
                    except PermissionError as exc:
                        st.error(str(exc))


def show_desk_dashboard() -> None:
    user = get_active_user()
    metrics = get_dashboard_metrics()
    st.markdown("### Desk head dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Published yesterday", str(metrics["published_yesterday"]), "Previous day")
    with col2:
        render_metric_card("Published today", str(metrics["published_today"]), "Current day")
    with col3:
        render_metric_card("Avg. publication lag", metrics["average_time_to_publish"], "From first source")
    with col4:
        render_metric_card("Awaiting editor", str(metrics["stories_awaiting_editor"]), "Open workload")

    rows = []
    for story in metrics["published"]:
        rows.append({
            "Story": story["title"],
            "Publication time": story.get("published_at", ""),
            "Time to publish": story.get("time_to_publish_human", "0m"),
            "Source count": story.get("source_count", 0),
            "Subject": story["title"],
        })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No published stories yet.")


def main() -> None:
    st.title("News Brief Desk")
    st.caption(app_title())
    users = get_all_users()
    user_names = {user["id"]: user for user in users}
    selected_index = st.sidebar.selectbox(
        "Select user",
        options=[user["id"] for user in users],
        format_func=lambda user_id: f"{user_names[user_id]['role']} — {user_names[user_id]['name']}",
        index=0,
    )
    st.session_state.selected_user = selected_index
    user = get_active_user()
    if user:
        st.sidebar.markdown(f"**Current role:** {nav_label(user['role'])}")
        st.sidebar.caption("Demo authentication only; production requires real auth.")

    nav = st.sidebar.radio("Navigation", ["Home", "Incoming", "Story Groups", "Drafts", "Editor Review", "Published", "Desk Dashboard"])
    if nav == "Home":
        show_home()
    elif nav == "Incoming":
        show_incoming()
    elif nav == "Story Groups":
        show_story_groups()
    elif nav == "Drafts":
        show_drafts()
    elif nav == "Editor Review":
        if user and user["role"] == "EDITOR":
            show_editor_review()
        else:
            st.warning("Only the editor can review and publish stories.")
    elif nav == "Published":
        show_published()
    elif nav == "Desk Dashboard":
        if user and user["role"] == "DESK_HEAD":
            show_desk_dashboard()
        else:
            st.warning("Only the desk head can view the desk dashboard.")


if __name__ == "__main__":
    main()
