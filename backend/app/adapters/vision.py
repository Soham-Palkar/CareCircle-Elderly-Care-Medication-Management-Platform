"""Vision adapter interface and implementations for prescription/strip extraction."""

from __future__ import annotations

import abc
from decimal import Decimal
from typing import Any

from app.core.config import get_settings


class VisionExtractor(abc.ABC):
    @abc.abstractmethod
    async def extract_label(self, image_bytes: bytes, mime_type: str) -> dict[str, Any]:
        """Extract name, strength, form, frequency, instructions, confidence."""
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_strip_match(
        self,
        image_bytes: bytes,
        mime_type: str,
        expected_name: str,
        expected_strength: str,
    ) -> dict[str, Any]:
        """Verify dose photo against scheduled medication label."""
        raise NotImplementedError


class FakeVisionExtractor(VisionExtractor):
    """Deterministic extractor for tests and local development."""

    async def extract_label(self, image_bytes: bytes, mime_type: str) -> dict[str, Any]:
        return {
            "name": "Metformin",
            "strength": "500 mg",
            "form": "tablet",
            "frequency": "Twice daily after meals",
            "instructions": "Take with breakfast and dinner with water.",
            "purpose_card": {
                "purpose": "Helps manage blood glucose levels.",
                "instructions": "Take with meals to minimize stomach upset.",
                "food_warning": "Avoid excessive alcohol intake.",
                "cautions": "Inform your doctor if experiencing persistent fatigue or nausea.",
                "disclaimer": "Advisory information only. Follow your prescribing doctor's exact instructions.",
            },
            "confidence": Decimal("0.92"),
        }

    async def verify_strip_match(
        self,
        image_bytes: bytes,
        mime_type: str,
        expected_name: str,
        expected_strength: str,
    ) -> dict[str, Any]:
        return {
            "match": True,
            "confidence": 0.95,
            "message": f"Confirmed: matches scheduled {expected_name} ({expected_strength}).",
        }


def get_vision_extractor() -> VisionExtractor:
    return FakeVisionExtractor()
