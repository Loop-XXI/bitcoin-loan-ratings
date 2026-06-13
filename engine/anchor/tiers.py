"""
Anchor Grade — Evidence Tier Discounting Module.

Each sub-signal score is discounted by a tier factor before pillar averaging,
reflecting the reliability of the evidence source:

    T1 (On-chain / Verifiable):     1.00
    T2 (Audit / Report):            0.90
    T3 (ToS / Documentation):       0.75
    T4 (Marketing / Unverified):    0.50
    T0 (No information):            Sub-signal scored flat 20, flagged 'Unverified'
"""

from __future__ import annotations

import enum
from typing import Final


class EvidenceTier(enum.Enum):
    """Evidence reliability tiers for sub-signal scoring."""

    T1 = "T1"
    """On-chain / directly verifiable evidence (factor = 1.00)."""

    T2 = "T2"
    """Audit or published report (factor = 0.90)."""

    T3 = "T3"
    """Terms of service or documentation (factor = 0.75)."""

    T4 = "T4"
    """Marketing material or unverifiable claims (factor = 0.50)."""

    T0 = "T0"
    """No information available — sub-signal scored flat 20, flagged 'Unverified'."""


# ── Multipliers ────────────────────────────────────────────────────────────

TIER_MULTIPLIERS: Final[dict[EvidenceTier, float]] = {
    EvidenceTier.T1: 1.00,
    EvidenceTier.T2: 0.90,
    EvidenceTier.T3: 0.75,
    EvidenceTier.T4: 0.50,
}

# For T0, we do NOT use a multiplier — the sub-signal is scored flat 20.
TIER_FLAT_SCORE_T0: Final[int] = 20


# ── Pure Functions ─────────────────────────────────────────────────────────

def compute_discounted_score(score: float, tier: EvidenceTier) -> float:
    """Apply the tier multiplier to a raw sub-signal score.

    For T0, returns *score* unchanged — the caller should use the flat
    20 directly instead.  This function handles the multiplier path only.

    Parameters
    ----------
    score:
        Raw sub-signal score (typically 0-100).
    tier:
        Evidence tier for this sub-signal.

    Returns
    -------
    Discounted score (score * multiplier).
    """
    if tier == EvidenceTier.T0:
        return score  # caller expected to substitute TIER_FLAT_SCORE_T0
    return score * TIER_MULTIPLIERS.get(tier, 1.0)
