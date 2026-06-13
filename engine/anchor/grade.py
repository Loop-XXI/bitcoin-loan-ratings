"""
Anchor Grade — Core Grading Engine.

The Anchor Grade scores Bitcoin-backed loan products on *safety* (not cost)
using five pillars with weighted geometric aggregation.
"""

from __future__ import annotations

import math
from typing import Any, Final

from .gates import gate_check
from .tiers import (
    TIER_FLAT_SCORE_T0,
    EvidenceTier,
    compute_discounted_score,
)

__all__ = ["AnchorGrader"]

# ── Pillar Configuration ──────────────────────────────────────────────────

PILLAR_NAMES: Final[list[str]] = [
    "Key Control & Exit",
    "Asset Fidelity",
    "Verifiability",
    "Operator Resilience",
    "Borrower Exposure",
]

PILLAR_IDS: Final[list[str]] = [
    "pillar_1",
    "pillar_2",
    "pillar_3",
    "pillar_4",
    "pillar_5",
]

PILLAR_WEIGHTS: Final[dict[str, float]] = {
    "pillar_1": 0.28,
    "pillar_2": 0.22,
    "pillar_3": 0.20,
    "pillar_4": 0.18,
    "pillar_5": 0.12,
}

# Sub-signal keys per pillar (for documentation / validation).
PILLAR_SUB_SIGNALS: Final[dict[str, list[str]]] = {
    "pillar_1": ["1a_arch", "1a_contract", "1b", "1c", "1d"],
    "pillar_2": ["2a", "2b", "2c"],
    "pillar_3": ["3a", "3b", "3c", "3d"],
    "pillar_4": ["4a", "4b", "4c", "4d"],
    "pillar_5": ["5a", "5b", "5c"],
}

# ── Grade Bands ───────────────────────────────────────────────────────────

GRADE_BANDS: Final[list[tuple[float, float, str]]] = [
    (92.0, 100.0, "A+"),
    (84.0, 91.99, "A"),
    (72.0, 83.99, "B"),
    (58.0, 71.99, "C"),
    (40.0, 57.99, "D"),
    (0.0, 39.99, "F"),
]

EPSILON: Final[float] = 1.0


# ── Pure Helpers ──────────────────────────────────────────────────────────

def _grade_letter(score: float) -> str:
    """Map a numerical anchor score to its letter grade."""
    for lo, hi, grade in GRADE_BANDS:
        if lo <= score <= hi:
            return grade
    return "F"  # fallback


# ── Anchor Grader ─────────────────────────────────────────────────────────

class AnchorGrader:
    """Deterministic Anchor Grade engine for Bitcoin-backed loan products.

    Usage::

        grader = AnchorGrader()
        result = grader.compute_all(evidence)
        # result == {
        #     "pillar_scores": {...},
        #     "anchor_score": 78.3,
        #     "grade_letter": "B",
        #     "gates": [],
        #     "sub_signal_details": {...},
        # }
    """

    # ── Public API ──────────────────────────────────────────────────────

    @staticmethod
    def compute_pillar_score(sub_signals: list[float]) -> float:
        """Compute a pillar score as the arithmetic mean of its sub-signals.

        Parameters
        ----------
        sub_signals:
            Raw (pre-discount) sub-signal scores in [0, 100].

        Returns
        -------
        Mean pillar score (float).
        """
        if not sub_signals:
            return 0.0
        return sum(sub_signals) / len(sub_signals)

    @staticmethod
    def compute_discounted_pillar(
        pillar_subs: dict[str, dict[str, Any]],
    ) -> float:
        """Apply evidence-tier discounting before averaging a pillar.

        Each sub-signal entry must have keys ``score`` (float) and
        ``tier`` (EvidenceTier).  T0 sub-signals are given the flat
        score ``TIER_FLAT_SCORE_T0`` (20) regardless of the supplied
        score.

        Parameters
        ----------
        pillar_subs:
            Mapping of sub-signal ID -> ``{"score": …, "tier": …}``.

        Returns
        -------
        Discounted pillar mean (float in [0, 100]).
        """
        discounted: list[float] = []
        for sub_id, entry in pillar_subs.items():
            raw = float(entry.get("score", 0))
            tier = entry.get("tier", EvidenceTier.T4)

            if tier == EvidenceTier.T0:
                discounted.append(float(TIER_FLAT_SCORE_T0))
            else:
                discounted.append(compute_discounted_score(raw, tier))

        if not discounted:
            return 0.0
        return sum(discounted) / len(discounted)

    @staticmethod
    def compute_anchor_score(pillar_scores: dict[str, float]) -> float:
        """Weighted geometric product of five pillar scores.

        Formula (from spec)::

            AnchorScore = 100 * prod(max(P_i, EPSILON) / 100) ** w_i

        where ``EPSILON = 1`` prevents a single zero pillar from
        collapsing the entire score to zero.

        Parameters
        ----------
        pillar_scores:
            Mapping of pillar ID -> score (post-discounting).

        Returns
        -------
        Anchor score (float in [0, 100]).
        """
        if not pillar_scores:
            return 0.0

        product = 1.0
        for pid in PILLAR_IDS:
            raw = pillar_scores.get(pid, 0.0)
            clamped = max(raw, EPSILON)
            w = PILLAR_WEIGHTS.get(pid, 0.0)
            product *= (clamped / 100.0) ** w

        return 100.0 * product

    @classmethod
    def compute_all(cls, evidence: dict[str, Any]) -> dict[str, Any]:
        """Full Anchor Grade computation from an evidence dict.

        Expected *evidence* structure::

            {
                "pillar_1": {
                    "1a": {"score": 75, "tier": EvidenceTier.T1},
                    "1b": {"score": 50, "tier": EvidenceTier.T2},
                    ...
                },
                "pillar_2": {...},
                "pillar_3": {...},
                "pillar_4": {...},
                "pillar_5": {...},
                "gates": {
                    "G1": False,
                    "G2": False,
                    ...
                }
            }

        Parameters
        ----------
        evidence:
            Full evidence dictionary (see above).

        Returns
        -------
        dict with keys:
            - ``pillar_scores``: dict[str, float]
            - ``anchor_score``: float
            - ``grade_letter``: str
            - ``gates``: list[str]
            - ``sub_signal_details``: dict[str, dict[str, dict]]
        """
        # 1. Check gates
        gates_data = evidence.get("gates", {})
        triggered_gates = gate_check(gates_data)

        # 2. Compute pillar scores (with tier discounting)
        pillar_scores: dict[str, float] = {}
        sub_signal_details: dict[str, dict[str, dict[str, Any]]] = {}

        for pid in PILLAR_IDS:
            pillar_evidence = evidence.get(pid, {})
            if not pillar_evidence:
                pillar_scores[pid] = 0.0
                sub_signal_details[pid] = {}
                continue

            # Record individual sub-signal details
            details: dict[str, dict[str, Any]] = {}
            for sub_id, entry in pillar_evidence.items():
                raw = float(entry.get("score", 0))
                tier = entry.get("tier", EvidenceTier.T4)
                discounted = (
                    float(TIER_FLAT_SCORE_T0)
                    if tier == EvidenceTier.T0
                    else compute_discounted_score(raw, tier)
                )
                details[sub_id] = {
                    "raw_score": raw,
                    "tier": tier.value,
                    "multiplier": (
                        0.0
                        if tier == EvidenceTier.T0
                        else (
                            1.00 if tier == EvidenceTier.T1
                            else 0.90 if tier == EvidenceTier.T2
                            else 0.75 if tier == EvidenceTier.T3
                            else 0.50
                        )
                    ),
                    "discounted_score": discounted,
                }

            sub_signal_details[pid] = details
            pillar_scores[pid] = cls.compute_discounted_pillar(pillar_evidence)

        # 3. Compute anchor score
        anchor_score = cls.compute_anchor_score(pillar_scores)

        # 4. Grade letter
        grade_letter = _grade_letter(anchor_score)

        return {
            "pillar_scores": pillar_scores,
            "anchor_score": anchor_score,
            "grade_letter": grade_letter,
            "gates": triggered_gates,
            "sub_signal_details": sub_signal_details,
        }
