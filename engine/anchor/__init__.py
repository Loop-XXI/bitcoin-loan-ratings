"""
Anchor Grade Engine — Bitcoin-backed loan safety rating system.

Exports the main :class:`AnchorGrader` class, evidence-tier helpers,
and gate-checking utilities.
"""

from __future__ import annotations

from .grade import AnchorGrader
from .tiers import TIER_FLAT_SCORE_T0, TIER_MULTIPLIERS, EvidenceTier, compute_discounted_score
from .gates import GATE_DESCRIPTIONS, GATE_IDS, gate_check

__all__ = [
    "AnchorGrader",
    "EvidenceTier",
    "TIER_MULTIPLIERS",
    "TIER_FLAT_SCORE_T0",
    "compute_discounted_score",
    "gate_check",
    "GATE_IDS",
    "GATE_DESCRIPTIONS",
]
