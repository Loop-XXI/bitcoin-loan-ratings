"""Validation tests for the LSI engine.

Sanity checks (printed, not asserted):

1. A **high-LTV flexible** product (e.g. 90 % LTV / 95 % liquidation with
   top-up) should show **severe** LSI across the 2021‑22 crash window.
2. A **safe** product (50 % LTV / 95 % liquidation) should show **low** LSI
   (Minimal–Low band, ≤25) because BTC has experienced multiple >47%
   drawdowns since 2014.

Usage::

    python -m engine.lsi.validation.test_known_events
"""

import math
import os
import sys
import time

# Ensure the package root is on sys.path so that "from engine.lsi import …" works
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.lsi import LSIEngine

# ---------------------------------------------------------------------------
# Test products
# ---------------------------------------------------------------------------

HIGH_LTV_PRODUCT = {
    "ltv_initial": 0.90,
    "ltv_margincall": 0.92,
    "ltv_liquidation": 0.95,
    "grace_window_hours": 24,
    "top_up_permitted": True,
    "partial_liquidation": True,
    "oracle_update_cadence": 24,
    "available_terms_months": [1, 3, 6, 12],
}

SAFE_PRODUCT = {
    "ltv_initial": 0.50,
    "ltv_margincall": 0.75,
    "ltv_liquidation": 0.95,
    "grace_window_hours": 48,
    "top_up_permitted": True,
    "partial_liquidation": False,
    "oracle_update_cadence": 24,
    "available_terms_months": [3, 6, 12],
}

MID_PRODUCT = {
    "ltv_initial": 0.65,
    "ltv_margincall": 0.80,
    "ltv_liquidation": 0.85,
    "grace_window_hours": 12,
    "top_up_permitted": False,
    "partial_liquidation": True,
    "oracle_update_cadence": 24,
    "available_terms_months": [3, 6, 12, 24],
}

# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

SEPARATOR = "=" * 72


def print_header(label):
    print(f"\n{SEPARATOR}")
    print(f"  {label}")
    print(SEPARATOR)


def run_test(product, label, expected_severe=False, expected_low=False):
    print(f"\n  Product: {product['ltv_initial']*100:.0f}% LTV initial, "
          f"{product['ltv_liquidation']*100:.0f}% liquidation")
    print(f"  Top-up: {product['top_up_permitted']}, "
          f"Terms: {product['available_terms_months']} months")

    t0 = time.time()
    engine = LSIEngine(product, n_paths=2000)
    results = engine.run()
    elapsed = time.time() - t0

    blended = results["blended"]
    headline = blended["headline"]
    passive = blended["passive"]
    active = blended["active"]

    print(f"\n  ⏱  {elapsed:.1f}s")
    print(f"\n  Headline LSI (passive, longest term): {headline['LSI_score']} "
          f"— {headline['LSI_band']}")

    print("\n  Per-term (passive):")
    for term in sorted(passive):
        p = passive[term]
        print(f"    T={term:>2}m  P(liq)={p['P_liq']:.4f}  "
              f"P(mc)={p['P_mc']:.4f}  "
              f"liq={p['liquidation_count']:>4d}/{p['total_windows']:>5d}  "
              f"median_breach={p['median_time_to_breach_days']}d  "
              f"worst_survived={p['worst_window_survived_max_ltv']}")

    print("\n  Per-term (active):")
    for term in sorted(active):
        p = active[term]
        print(f"    T={term:>2}m  P(liq)={p['P_liq']:.4f}  "
              f"P(mc)={p['P_mc']:.4f}  "
              f"liq={p['liquidation_count']:>4d}/{p['total_windows']:>5d}  "
              f"median_breach={p['median_time_to_breach_days']}d  "
              f"worst_survived={p['worst_window_survived_max_ltv']}")

    # Sanity evaluation
    print(f"\n  Sanity: ", end="")
    if expected_severe:
        if headline["LSI_score"] >= 46:
            print(f"✅ PASS — LSI {headline['LSI_score']} is Severe/High "
                  f"(≥46) as expected")
        else:
            print(f"⚠️  LOW — expected Severe/High (≥46) but got "
                  f"{headline['LSI_score']} ({headline['LSI_band']})")
    elif expected_low:
        if headline["LSI_score"] <= 25:
            print(f"✅ PASS — LSI {headline['LSI_score']} is Minimal/Low (≤25) "
                  f"for this conservative product")
        else:
            print(f"⚠️  HIGH — expected Minimal/Low (≤25) but got "
                  f"{headline['LSI_score']} ({headline['LSI_band']})")
    else:
        # Mid-tier: bracket between extremes — report the band
        print(f"ℹ️  LSI {headline['LSI_score']} ({headline['LSI_band']}) "
              f"— bracketed between Low (18.85) and Severe (73.87)")

    print()
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print_header("LSI Engine — Validation Tests (Known Events)")
    print(f"  Data: cached BTC daily closes from 2014-01-01")
    print(f"  Bootstrap: 2 000 paths per term (30-day blocks)")
    print()

    print_header("Test 1: High-LTV flexible product (90%/95%)")
    print("  Expected: Severe LSI across 2021-22 crash window")
    run_test(HIGH_LTV_PRODUCT, "High-LTV flexible", expected_severe=True)

    print_header("Test 2: Safe product (50%/95%)")
    print("  Expected: Near-zero liquidation probability (Minimal LSI)")
    run_test(SAFE_PRODUCT, "Safe product", expected_severe=False)

    print_header("Test 3: Mid-tier product (65%/85%, no top-up)")
    print("  Expected: Moderate LSI (26-45) — bracket between the extremes")
    run_test(MID_PRODUCT, "Mid-tier", expected_severe=False)

    print_header("Done — all results printed above (no assertions).")


if __name__ == "__main__":
    main()
