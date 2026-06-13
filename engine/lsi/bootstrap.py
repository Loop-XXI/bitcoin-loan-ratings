"""BootstrapEngine — stationary block bootstrap for forward-looking liquidation
probability estimation.
"""

import math
import random


def stationary_block_bootstrap(
    log_returns,
    block_length=30,
    n_paths=10000,
    terms_months=None,
    ltv_params=None,
):
    """Run a stationary block bootstrap to estimate forward-looking liquidation
    probabilities for each loan term.

    Parameters
    ----------
    log_returns : list[float]
        Daily log returns from historical BTC prices.
    block_length : int
        Block size for the bootstrap (default 30 days).
    n_paths : int
        Number of bootstrap price paths to simulate (default 10 000).
    terms_months : list[int]
        Loan terms in months.
    ltv_params : dict
        Keys: ``ltv_initial``, ``ltv_margincall``, ``ltv_liquidation``,
        ``grace_window_hours``, ``top_up_permitted``.

    Returns
    -------
    dict[int, dict]
        Per-term results::

            {
                term_months: {
                    "liquidation_probability": float,
                    "margin_call_probability": float,
                },
                ...
            }
    """
    if terms_months is None:
        terms_months = [3, 6, 12, 24]
    if ltv_params is None:
        ltv_params = {}

    ltv_i = ltv_params.get("ltv_initial", 0.65)
    ltv_mc = ltv_params.get("ltv_margincall", 0.80)
    ltv_liq = ltv_params.get("ltv_liquidation", 0.85)
    grace_hrs = ltv_params.get("grace_window_hours", 24)
    top_up = ltv_params.get("top_up_permitted", False)

    grace_days = max(1, math.ceil(grace_hrs / 24))

    n = len(log_returns)
    if n == 0:
        return {t: {"liquidation_probability": 0.0, "margin_call_probability": 0.0}
                for t in terms_months}

    max_term_days = max(terms_months) * 30

    # Pre-compute cumulative log-return thresholds for fast checking.
    # Liquidation when cumulative_return <= ln(LTV_initial / LTV_liquidation)
    liq_threshold = math.log(ltv_i / ltv_liq) if ltv_liq > 0 else -float("inf")
    mc_threshold = math.log(ltv_i / ltv_mc) if ltv_mc > 0 else -float("inf")

    results = {}
    for term in terms_months:
        term_days = term * 30

        # For each path we need term_days of returns
        # Use block bootstrap: randomly sample overlapping blocks
        max_start = n - block_length
        if max_start <= 0:
            results[term] = {
                "liquidation_probability": 0.0,
                "margin_call_probability": 0.0,
            }
            continue

        liq_count = 0
        mc_count = 0

        for _ in range(n_paths):
            # Generate a path of returns of length term_days via block bootstrap
            path_ret = []
            while len(path_ret) < term_days:
                start_idx = random.randint(0, max_start)
                path_ret.extend(log_returns[start_idx: start_idx + block_length])

            # Trim to exact term length
            path_ret = path_ret[:term_days]

            # Cumulative sum (log returns are additive)
            cum = 0.0
            liq_in_path = False
            mc_in_path = False

            for r in path_ret:
                cum += r
                if not mc_in_path and cum <= mc_threshold:
                    mc_in_path = True
                if not liq_in_path and cum <= liq_threshold:
                    # Active model grace window check:
                    # For active model with top-up, we need to check if the
                    # cumulative return recovers above the threshold within
                    # grace_days.
                    if top_up:
                        # Check if within the next grace_days steps the cum
                        # recovers above liq_threshold.
                        # We can't look ahead easily, so approximate:
                        # Check the next grace_days returns
                        idx = path_ret.index(r)  # first occurrence of this r
                        recovery = False
                        for j in range(1, grace_days + 1):
                            look = idx + j
                            if look >= len(path_ret):
                                break
                            # recalculate cumulative at look
                            c2 = sum(path_ret[:look + 1])
                            if c2 > liq_threshold:
                                recovery = True
                                break
                        if not recovery:
                            liq_in_path = True
                    else:
                        liq_in_path = True

            if liq_in_path:
                liq_count += 1
            if mc_in_path:
                mc_count += 1

        results[term] = {
            "liquidation_probability": liq_count / n_paths,
            "margin_call_probability": mc_count / n_paths,
        }

    return results
