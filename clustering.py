from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from utils.helpers import normalize_text


def text_tokens(value: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(value))


def jaccard_similarity(a: str, b: str) -> float:
    tokens_a = set(text_tokens(a))
    tokens_b = set(text_tokens(b))
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def same_event_score(item_a: dict, item_b: dict) -> float:
    headline_score = jaccard_similarity(item_a["headline"], item_b["headline"])
    content_score = jaccard_similarity(item_a["content"], item_b["content"])
    a_text = normalize_text(item_a["headline"] + " " + item_a["content"])
    b_text = normalize_text(item_b["headline"] + " " + item_b["content"])
    overlap = set(a_text.split()) & set(b_text.split())
    keywords = {"bengaluru", "chennai", "metro", "signal", "signalling", "services", "delay", "flood", "coastal", "rain", "storm"}
    keyword_hits = len(overlap & keywords)

    city_a = None
    city_b = None
    for city in ("bengaluru", "chennai", "mumbai", "delhi", "hyderabad", "kochi"):
        if city in a_text:
            city_a = city
        if city in b_text:
            city_b = city

    location_match = city_a == city_b
    if city_a and city_b and not location_match:
        return 0.0

    location_bonus = 0.12 if location_match else 0.0
    if item_a["source_name"] == item_b["source_name"]:
        location_bonus += 0.02

    base = headline_score * 0.55 + content_score * 0.25 + min(keyword_hits * 0.08, 0.15) + location_bonus
    return min(1.0, base)


def build_suggested_groups(raw_items: Iterable[dict]) -> List[dict]:
    items = list(raw_items)
    groups: List[List[dict]] = []
    remaining = list(items)
    while remaining:
        current = remaining.pop(0)
        group = [current]
        for candidate in list(remaining):
            score = same_event_score(current, candidate)
            if score >= 0.32:
                group.append(candidate)
                remaining.remove(candidate)
        groups.append(group)

    results = []
    for group in groups:
        if len(group) == 1:
            results.append({
                "id": f"group-{len(results)+1}",
                "items": group,
                "reason": "Standalone item — no close duplicate match found.",
                "confidence": "low",
            })
            continue
        reasons = []
        headline_overlap = max(jaccard_similarity(group[0]["headline"], item["headline"]) for item in group[1:])
        if headline_overlap >= 0.25:
            reasons.append("High headline similarity")
        if any("metro" in normalize_text(item["headline"] + " " + item["content"]) for item in group):
            reasons.append("Same location and transport context")
        if len(group) >= 3:
            reasons.append("Multiple sources reporting same event")
        if not reasons:
            reasons.append("Likely duplicate cluster")
        results.append({
            "id": f"group-{len(results)+1}",
            "items": group,
            "reason": "; ".join(reasons),
            "confidence": "medium" if len(group) >= 2 else "low",
        })
    return results


def best_group_for_raw_item(raw_items: Iterable[dict], target: dict) -> List[dict]:
    groups = build_suggested_groups(raw_items)
    for group in groups:
        if any(item["id"] == target["id"] for item in group["items"]):
            return group["items"]
    return [target]


def cluster_candidates(raw_items: Iterable[dict]) -> Dict[str, List[int]]:
    groups = build_suggested_groups(raw_items)
    mapping: Dict[str, List[int]] = {}
    for index, group in enumerate(groups, start=1):
        mapping[f"group-{index}"] = [item["id"] for item in group["items"]]
    return mapping
