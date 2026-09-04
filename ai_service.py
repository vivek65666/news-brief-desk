from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


def get_openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "")


def has_ai_configured() -> bool:
    return bool(get_openai_api_key())


def generate_brief_from_sources(title: str, source_items: List[dict]) -> tuple[str, str]:
    if not source_items:
        return "No source material available for a draft brief.", "fallback"

    if has_ai_configured():
        try:
            from openai import OpenAI

            client = OpenAI(api_key=get_openai_api_key())
            prompt = (
                "Write a concise newsroom brief based only on the supplied source material. "
                "Keep it to 2-3 sentences, mention location if relevant, avoid making up facts, and include the key event.\n\n"
                + "\n\n".join(
                    f"Source: {item['source_name']} | Headline: {item['headline']} | Content: {item['content']}"
                    for item in source_items
                )
            )
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
            )
            text = response.output_text.strip()
            if text:
                return text, "ai"
        except Exception:
            pass

    text = summarize_fallback(source_items)
    return text, "fallback"


def summarize_fallback(source_items: List[dict]) -> str:
    if not source_items:
        return "No source material available for a draft brief."

    combined = source_items[0]
    headline = combined["headline"]
    content_bits = [item["content"] for item in source_items[:3]]
    intro = headline
    if len(source_items) > 1:
        intro = headline
    sentence = " ".join(content_bits)
    first_sent = sentence.split(". ")[0].strip()
    if len(first_sent) < 40:
        first_sent = headline
    brief = first_sent
    if len(brief) > 180:
        brief = brief[:177].rstrip() + "..."
    return brief
