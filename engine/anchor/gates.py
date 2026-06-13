"""
Anchor Grade — Gate Check Module.

Gates are binary conditions that, if any are triggered, cause the loan
product to be marked GATED (not scored).  Each gate is checked against
a provider-data dictionary supplied by the analyst.

Gates
-----
G1 — Confirmed unremediated loss of customer funds
G2 — Active fraud findings / litigation
G3 — Unrestricted undisclosed rehypothecation (implies 2b = 0 at ≤T3)
G4 — Single-key or undisclosed unilateral custody
G5 — No enforceable / script-based claim to collateral
"""

from __future__ import annotations

from typing import Any

# ── Gate Identifiers ──────────────────────────────────────────────────────

GATE_IDS: list[str] = ["G1", "G2", "G3", "G4", "G5"]

GATE_DESCRIPTIONS: dict[str, str] = {
    "G1": "Confirmed unremediated loss of customer funds",
    "G2": "Active fraud findings / litigation",
    "G3": "Unrestricted undisclosed rehypothecation",
    "G4": "Single-key or undisclosed unilateral custody",
    "G5": "No enforceable / script-based claim to collateral",
}


# ── Pure Functions ─────────────────────────────────────────────────────────

def gate_check(provider_data: dict[str, Any]) -> list[str]:
    """Check *provider_data* against all five gates.

    The caller supplies a flat dict with boolean keys (or keys that
    coerce to bool) indicating whether each gate condition is true::

        {
            "G1": False,
            "G2": False,
            "G3": False,
            "G4": True,   # single-key custody triggers G4
            "G5": False,
        }

    Keys that are absent are treated as ``False`` (gate not triggered).

    Parameters
    ----------
    provider_data:
        Arbitrary dict; only keys matching ``G1``-``G5`` are inspected.

    Returns
    -------
    List of triggered gate IDs (e.g. ``["G4"]``).  Empty list = no gates.
    """
    return [gid for gid in GATE_IDS if bool(provider_data.get(gid, False))]
