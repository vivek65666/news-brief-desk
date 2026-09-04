from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, List, Optional

from news_data import SAMPLE_RAW_ITEMS

DB_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DB_DIR / "news.db"


def ensure_db_dir() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    ensure_db_dir()
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('REPORTER','EDITOR','DESK_HEAD'))
            );

            CREATE TABLE IF NOT EXISTS raw_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                headline TEXT NOT NULL,
                content TEXT NOT NULL,
                received_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'INCOMING'
            );

            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                published_at TEXT,
                reporter_id INTEGER,
                editor_id INTEGER,
                brief_source TEXT NOT NULL DEFAULT 'fallback',
                FOREIGN KEY (reporter_id) REFERENCES users(id),
                FOREIGN KEY (editor_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS story_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                raw_item_id INTEGER NOT NULL,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                FOREIGN KEY (raw_item_id) REFERENCES raw_items(id) ON DELETE CASCADE,
                UNIQUE(story_id, raw_item_id)
            );

            CREATE TABLE IF NOT EXISTS story_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                user_id INTEGER,
                timestamp TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        migrate_story_schema(conn)
        seed_users(conn)
        refresh_demo_seed_if_needed(conn)
        seed_demo_published_stories(conn)


def refresh_demo_seed_if_needed(conn: sqlite3.Connection) -> None:
    raw_rows = conn.execute(
        "SELECT received_at FROM raw_items ORDER BY received_at DESC LIMIT 20"
    ).fetchall()

    if not raw_rows:
        seed_raw_items(conn)
        return

    newest = max(row["received_at"] for row in raw_rows)
    newest_dt = datetime.fromisoformat(newest.replace("Z", "+00:00"))
    if newest_dt >= datetime.now(timezone.utc) - timedelta(days=2):
        return

    conn.execute("DELETE FROM story_history")
    conn.execute("DELETE FROM story_sources")
    conn.execute("DELETE FROM stories")
    conn.execute("DELETE FROM raw_items")
    conn.execute("DELETE FROM users")
    seed_users(conn)
    seed_raw_items(conn)


def migrate_story_schema(conn: sqlite3.Connection) -> None:
    columns = [row[1] for row in conn.execute("PRAGMA table_info(stories)").fetchall()]
    if "brief_source" not in columns:
        conn.execute("ALTER TABLE stories ADD COLUMN brief_source TEXT NOT NULL DEFAULT 'fallback'")


def seed_users(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if existing > 0:
        return
    rows = [
        ("Asha Menon", "REPORTER"),
        ("Rahul Sharma", "EDITOR"),
        ("Meera Iyer", "DESK_HEAD"),
    ]
    conn.executemany("INSERT INTO users (name, role) VALUES (?, ?)", rows)


def seed_raw_items(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) AS c FROM raw_items").fetchone()["c"]
    if existing > 0:
        return
    rows = []
    for item in SAMPLE_RAW_ITEMS:
        rows.append(
            (
                item["source_name"],
                item["source_type"],
                item["headline"],
                item["content"],
                item["received_at"],
                item.get("status", "INCOMING"),
            )
        )
    conn.executemany(
        "INSERT INTO raw_items (source_name, source_type, headline, content, received_at, status) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def seed_demo_published_stories(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) AS c FROM stories WHERE status = 'PUBLISHED'").fetchone()["c"] > 0:
        return

    user_rows = conn.execute("SELECT id, role FROM users ORDER BY id").fetchall()
    if not user_rows:
        return

    reporter_id = next((row["id"] for row in user_rows if row["role"] == "REPORTER"), user_rows[0]["id"])
    editor_id = next((row["id"] for row in user_rows if row["role"] == "EDITOR"), user_rows[0]["id"])
    raw_rows = conn.execute("SELECT id, received_at FROM raw_items ORDER BY received_at ASC").fetchall()
    if len(raw_rows) < 4:
        return

    now = datetime.now(timezone.utc)
    published_story_specs = [
        {
            "title": "Bengaluru Metro signal fault disrupts Purple Line commutes",
            "summary": "Authorities restored limited service after a signal fault disrupted the Purple Line during the morning rush, with commuters advised to expect delays and crowding.",
            "published_at": (now - timedelta(days=1, hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "story_sources": [0, 1, 2],
        },
        {
            "title": "Flood relief teams expand support in coastal villages",
            "summary": "Relief teams continued road clearance and emergency food distribution after heavy monsoon rain left several villages cut off.",
            "published_at": (now - timedelta(days=1, hours=8)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "story_sources": [12, 13, 14],
        },
        {
            "title": "Hospital network adds emergency beds amid seasonal demand",
            "summary": "Health providers widened capacity as seasonal illness cases rose, with queue and triage pressure continuing across city facilities.",
            "published_at": (now - timedelta(days=0, hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "story_sources": [15, 16],
        },
    ]

    for spec in published_story_specs:
        story_id = conn.execute(
            """
            INSERT INTO stories (title, summary, status, created_at, updated_at, published_at, reporter_id, editor_id, brief_source)
            VALUES (?, ?, 'PUBLISHED', ?, ?, ?, ?, ?, 'fallback')
            """,
            (
                spec["title"],
                spec["summary"],
                spec["published_at"],
                spec["published_at"],
                spec["published_at"],
                reporter_id,
                editor_id,
            ),
        ).lastrowid
        for source_index in spec["story_sources"]:
            raw_item_id = raw_rows[source_index]["id"]
            conn.execute(
                "INSERT OR IGNORE INTO story_sources (story_id, raw_item_id) VALUES (?, ?)",
                (story_id, raw_item_id),
            )
        conn.execute(
            "INSERT INTO story_history (story_id, action, user_id, timestamp, details) VALUES (?, ?, ?, ?, ?)",
            (story_id, "PUBLISHED", editor_id, spec["published_at"], "Seeded published demo story."),
        )


def get_all_users() -> List[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()]


def get_user_by_id(user_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_role(role: str) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM users WHERE role = ? ORDER BY id ASC", (role,)).fetchall()
        return [dict(row) for row in rows]


def get_raw_items() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM raw_items ORDER BY received_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_raw_item(raw_item_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM raw_items WHERE id = ?", (raw_item_id,)).fetchone()
        return dict(row) if row else None


def update_raw_item_status(raw_item_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE raw_items SET status = ? WHERE id = ?", (status, raw_item_id))


def get_story_by_id(story_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
        return dict(row) if row else None


def get_story_sources(story_id: int) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT r.*
            FROM story_sources ss
            JOIN raw_items r ON r.id = ss.raw_item_id
            WHERE ss.story_id = ?
            ORDER BY r.received_at ASC
            """,
            (story_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_all_stories() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM stories ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def insert_story(title: str, summary: str, reporter_id: int, status: str = "DRAFT", brief_source: str = "fallback") -> int:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO stories (title, summary, status, created_at, updated_at, published_at, reporter_id, editor_id, brief_source)
            VALUES (?, ?, ?, ?, ?, NULL, ?, NULL, ?)
            """,
            (title, summary, status, now, now, reporter_id, brief_source),
        )
        return int(cursor.lastrowid)


def update_story(story_id: int, **updates: Any) -> None:
    from datetime import datetime, timezone

    valid_fields = {"title", "summary", "status", "published_at", "reporter_id", "editor_id", "brief_source"}
    if not updates:
        return
    fields = []
    values = []
    for key, value in updates.items():
        if key not in valid_fields:
            continue
        fields.append(f"{key} = ?")
        values.append(value)
    if not fields:
        return
    values.append(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    values.append(story_id)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE stories SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
            values,
        )


def add_story_source(story_id: int, raw_item_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO story_sources (story_id, raw_item_id) VALUES (?, ?)",
            (story_id, raw_item_id),
        )


def log_story_history(story_id: int, action: str, user_id: Optional[int], details: str) -> None:
    from datetime import datetime, timezone

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO story_history (story_id, action, user_id, timestamp, details) VALUES (?, ?, ?, ?, ?)",
            (story_id, action, user_id, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), details),
        )


def get_story_history(story_id: int) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM story_history WHERE story_id = ? ORDER BY timestamp DESC, id DESC",
            (story_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_story_sources_count(story_id: int) -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM story_sources WHERE story_id = ?", (story_id,)).fetchone()
        return int(row["c"])


def reset_demo_data() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM story_history")
        conn.execute("DELETE FROM story_sources")
        conn.execute("DELETE FROM stories")
        conn.execute("DELETE FROM raw_items")
        conn.execute("DELETE FROM users")
        seed_users(conn)
        seed_raw_items(conn)


def initialize_app() -> None:
    init_db()
