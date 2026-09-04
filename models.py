from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class User:
    id: int
    name: str
    role: str


@dataclass
class RawItem:
    id: int
    source_name: str
    source_type: str
    headline: str
    content: str
    received_at: str
    status: str = "INCOMING"


@dataclass
class Story:
    id: int
    title: str
    summary: str
    status: str
    created_at: str
    updated_at: str
    published_at: Optional[str]
    reporter_id: int
    editor_id: Optional[int]
    sources: Optional[List[RawItem]] = None
