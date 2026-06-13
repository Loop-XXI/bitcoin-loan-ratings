"""blend — combine historical backtest results with bootstrap projections to
produce the final per-term P(liq) and the headline Liquidation Stress Index.
"""


LSI_BANDS = [
    (0, 10, "Minimal"),
    (11, 25, "Low"),
    (26, 45, "Moderate"),
    (46, 70, "High"),
    (71, 100, "Severe"),
]


def _lsi_band(score):
    """Return the label for an LSI score (0-100)."""
    for lo, hi, label in LSI_BANDS:
        if lo <= score <= hi:
            return label
    return "Unknown"


def blend(historical_results, bootstrap_results):
    """Blend historical and bootstrap results into final per-term statistics.

    Parameters
    ----------
    historical_results : dict[str, dict[int, dict]]
        ``{"passive": {term: {...}}, "active": {term: {...}}}`` as returned by
        :meth:`BacktestEngine.simulate`.
    bootstrap_results : dict[int, dict]
        ``{term: {"liquidation_probability": float, ...}}`` as returned by
        :func:`stationary_block_bootstrap`.

    Returns
    -------
    dict
        ::

            {
                "passive": {
                    term_months: {
                        "P_liq": float,       # blended probability
                        "P_mc": float,         # historical margin-call prob
                        "liquidation_count": int,
                        "margin_call_count": int,
                        "total_windows": int,
                        "median_time_to_breach_days": float | None,
                        "worst_window_survived_max_ltv": float | None,
                        "bootstrap_P_liq": float,
                    },
                    ...
                },
                "active": { ... same structure ... },
                "headline": {
                    "term": int,
                    "model": str,
                    "P_liq": float,
                    "LSI_score": float,
                    "LSI_band": str,
                },
                "all_terms": [int, ...],
            }
    """
    # Determine overlapping terms
    hist_passive = historical_results.get("passive", {})
    hist_active = historical_results.get("active", {})

    # Bootstrap results should cover the same terms
    all_terms = sorted(set(hist_passive.keys()) | set(bootstrap_results.keys()))
    if not all_terms:
        return {"passive": {}, "active": {}, "headline": None, "all_terms": []}

    passive_out = {}
    active_out = {}

    for term in all_terms:
        h_pass = hist_passive.get(term, {})
        h_act = hist_active.get(term, {})
        b = bootstrap_results.get(term, {})

        total_windows = h_pass.get("total_windows", 0)

        # --- passive ---
        p_hist_pass = (h_pass.get("liquidation_count", 0) / total_windows
                       if total_windows > 0 else 0.0)
        p_boot = b.get("liquidation_probability", 0.0)
        p_liq_pass = 0.5 * p_hist_pass + 0.5 * p_boot

        p_mc_hist_pass = (h_pass.get("margin_call_count", 0) / total_windows
                          if total_windows > 0 else 0.0)

        passive_out[term] = {
            "P_liq": p_liq_pass,
            "P_mc": p_mc_hist_pass,
            "liquidation_count": h_pass.get("liquidation_count", 0),
            "margin_call_count": h_pass.get("margin_call_count", 0),
            "total_windows": total_windows,
            "median_time_to_breach_days": h_pass.get(
                "median_time_to_breach_days"),
            "worst_window_survived_max_ltv": h_pass.get(
                "worst_window_survived_max_ltv"),
            "bootstrap_P_liq": p_boot,
        }

        # --- active ---
        total_windows_act = h_act.get("total_windows", 0)
        p_hist_act = (h_act.get("liquidation_count", 0) / total_windows_act
                      if total_windows_act > 0 else 0.0)
        p_liq_act = 0.5 * p_hist_act + 0.5 * p_boot

        p_mc_hist_act = (h_act.get("margin_call_count", 0) / total_windows_act
                         if total_windows_act > 0 else 0.0)

        active_out[term] = {
            "P_liq": p_liq_act,
            "P_mc": p_mc_hist_act,
            "liquidation_count": h_act.get("liquidation_count", 0),
            "margin_call_count": h_act.get("margin_call_count", 0),
            "total_windows": total_windows_act,
            "median_time_to_breach_days": h_act.get(
                "median_time_to_breach_days"),
            "worst_window_survived_max_ltv": h_act.get(
                "worst_window_survived_max_ltv"),
            "bootstrap_P_liq": p_boot,
        }

    # --- Headline LSI ---
    # Use the *longest standard term* for the headline, with the *passive* model.
    longest_term = max(passive_out.keys())
    headline_p_liq = passive_out[longest_term]["P_liq"]
    headline_score = round(100.0 * headline_p_liq, 2)
    headline_band = _lsi_band(headline_score)

    return {
        "passive": passive_out,
        "active": active_out,
        "headline": {
            "term": longest_term,
            "model": "passive",
            "P_liq": headline_p_liq,
            "LSI_score": headline_score,
            "LSI_band": headline_band,
        },
        "all_terms": all_terms,
    }
