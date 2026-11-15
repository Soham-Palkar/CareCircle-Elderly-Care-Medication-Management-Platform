"""intents.py — Deterministic keyword and regex intent recognition (English + Hindi).

No external LLM or cloud API is needed for core voice commands.
Fast, offline-resilient, and predictable.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from app.domain.types import Intent


class PatternDef(NamedTuple):
    name: str
    patterns: list[str]
    confidence: float


INTENT_PATTERNS: list[PatternDef] = [
    PatternDef(
        name="taken",
        patterns=[
            r"\b(taken|took|taken it|i took it|done|yes taken|all taken)\b",
            r"\b(le liya|dawai le li|le li|kha liya|khaya)\b",
        ],
        confidence=0.95,
    ),
    PatternDef(
        name="later",
        patterns=[
            r"\b(later|snooze|remind me later|not now|in a bit|wait)\b",
            r"\b(baad mein|baad me|thodi der mein|ruko|abhi nahi)\b",
        ],
        confidence=0.95,
    ),
    PatternDef(
        name="next_dose",
        patterns=[
            r"\b(next|next dose|what is next|when is next|what time)\b",
            r"\b(agli|agla|agle|kab lena hai|agla samay)\b",
        ],
        confidence=0.90,
    ),
    PatternDef(
        name="what_for",
        patterns=[
            r"\b(what for|what is this for|why|purpose|what medicine)\b",
            r"\b(kisliye|kis kaam|kya fayda|kis bimari)\b",
        ],
        confidence=0.90,
    ),
    PatternDef(
        name="repeat",
        patterns=[
            r"\b(repeat|say again|again|pardon|one more time)\b",
            r"\b(dobara|phir se|phir bolo|dobara bolo)\b",
        ],
        confidence=0.95,
    ),
    PatternDef(
        name="help",
        patterns=[
            r"\b(help|emergency|alert|call caretaker|need help|pain|trouble)\b",
            r"\b(madad|madad chahiye|emergency|doctor ko bulao|dard)\b",
        ],
        confidence=0.98,
    ),
]


def match_intent(text: str, language_hint: str = "en") -> Intent:
    """Classify free text or speech-to-text transcript into a known intent."""
    cleaned = text.strip().lower()

    if not cleaned:
        return Intent(name="unknown", confidence=0.0, params={})

    for item in INTENT_PATTERNS:
        for pat in item.patterns:
            if re.search(pat, cleaned, re.IGNORECASE):
                return Intent(name=item.name, confidence=item.confidence, params={"raw_text": text})

    return Intent(name="unknown", confidence=0.1, params={"raw_text": text})
