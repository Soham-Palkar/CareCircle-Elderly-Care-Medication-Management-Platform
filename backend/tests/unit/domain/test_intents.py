"""Unit tests for deterministic keyword and regex intent recognition (English + Hindi)."""

import pytest
from app.domain.intents import match_intent


def test_intent_taken_english():
    queries = ["I took it", "Taken", "yes taken", "took my pill", "all taken", "done"]
    for q in queries:
        intent = match_intent(q, language_hint="en")
        assert intent.name == "taken", f"Failed for '{q}'"
        assert intent.confidence >= 0.90


def test_intent_taken_hindi():
    queries = ["le liya", "dawai le li", "kha liya", "khaya"]
    for q in queries:
        intent = match_intent(q, language_hint="hi")
        assert intent.name == "taken", f"Failed for Hindi '{q}'"
        assert intent.confidence >= 0.90


def test_intent_later_english_and_hindi():
    for q in ["remind me later", "snooze", "in a bit", "not now"]:
        intent = match_intent(q)
        assert intent.name == "later"

    for q in ["baad mein", "thodi der mein", "ruko", "abhi nahi"]:
        intent = match_intent(q, language_hint="hi")
        assert intent.name == "later"


def test_intent_next_dose():
    for q in ["what is next", "when is next", "what time is next dose"]:
        intent = match_intent(q)
        assert intent.name == "next_dose"

    for q in ["agli dawai kab hai", "agla samay"]:
        intent = match_intent(q, language_hint="hi")
        assert intent.name == "next_dose"


def test_intent_what_for():
    for q in ["what is this for", "what medicine is this", "purpose"]:
        intent = match_intent(q)
        assert intent.name == "what_for"

    for q in ["kisliye hai", "kya fayda"]:
        intent = match_intent(q, language_hint="hi")
        assert intent.name == "what_for"


def test_intent_help():
    for q in ["help", "emergency", "call caretaker", "need help"]:
        intent = match_intent(q)
        assert intent.name == "help"
        assert intent.confidence >= 0.95

    for q in ["madad chahiye", "emergency hai", "dard"]:
        intent = match_intent(q, language_hint="hi")
        assert intent.name == "help"


def test_unknown_intent():
    intent = match_intent("what is the weather in Delhi?")
    assert intent.name == "unknown"
    assert intent.confidence < 0.50

    empty = match_intent("")
    assert empty.name == "unknown"
    assert empty.confidence == 0.0
