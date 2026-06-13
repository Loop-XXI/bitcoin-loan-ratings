"""LSI Engine — Liquidation Stress Index for bitcoin-backed loans.

Usage
-----
>>> from engine.lsi import LSIEngine
>>> engine = LSIEngine(product_params={...})
>>> results = engine.run()
>>> print(results["blended"]["headline"]["LSI_score"])
"""

from engine.lsi.backtest import BacktestEngine, compute_log_returns, fetch_btc_data
from engine.lsi.blend import blend
from engine.lsi.bootstrap import stationary_block_bootstrap


class LSIEngine:
    """Orchestrates the full LSI computation pipeline.

    Parameters
    ----------
    product_params : dict
        Loan product parameters.  Required keys:

        - ``ltv_initial`` (float) — initial LTV ratio, e.g. ``0.65``.
        - ``ltv_margincall`` (float) — LTV that triggers a margin call.
        - ``ltv_liquidation`` (float) — LTV that triggers liquidation.
        - ``grace_window_hours`` (int) — hours of grace after a breach.
        - ``top_up_permitted`` (bool) — can the borrower add collateral?
        - ``partial_liquidation`` (bool) — is partial liquidation allowed?
        - ``oracle_update_cadence`` (int) — oracle price update interval hours.
        - ``available_terms_months`` (list[int]) — e.g. ``[3, 6, 12, 24]``.

    bootstrap_kw : dict, optional
        Extra keyword arguments forwarded to
        :func:`~engine.lsi.bootstrap.stationary_block_bootstrap` (e.g.
        ``n_paths``, ``block_length``).
    """

    def __init__(self, product_params, **bootstrap_kw):
        self.product_params = product_params
        self._bootstrap_kw = bootstrap_kw

        self.prices = None
        self.log_returns = None
        self.backtest_results = None
        self.bootstrap_results = None
        self.blended_results = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self):
        """Run the full LSI pipeline: fetch data → backtest → bootstrap → blend.

        Returns
        -------
        dict
            ::

                {
                    "product_params": {...},
                    "backtest": {"passive": {...}, "active": {...}},
                    "bootstrap": {term: {"liquidation_probability": ..., ...}},
                    "blended": {  # see blend.blend() return docs
                        "passive": {...},
                        "active": {...},
                        "headline": {"LSI_score": ..., "LSI_band": ...},
                        "all_terms": [...],
                    },
                }
        """
        self._fetch_data()
        self._run_backtest()
        self._run_bootstrap()
        self._run_blend()
        return self.results()

    def results(self):
        """Return the full results dictionary from the last run.

        Returns ``None`` if :meth:`run` has not been called yet.
        """
        if self.blended_results is None:
            return None

        return {
            "product_params": self.product_params,
            "backtest": self.backtest_results,
            "bootstrap": self.bootstrap_results,
            "blended": self.blended_results,
        }

    # ------------------------------------------------------------------
    # Internal steps
    # ------------------------------------------------------------------

    def _fetch_data(self):
        raw = fetch_btc_data()
        self.prices = raw
        self.log_returns = compute_log_returns(raw)

    def _run_backtest(self):
        engine = BacktestEngine(self.prices)
        self.backtest_results = {
            "passive": engine.simulate(self.product_params, "passive"),
            "active": engine.simulate(self.product_params, "active"),
        }

    def _run_bootstrap(self):
        kwargs = dict(self._bootstrap_kw)
        kwargs.setdefault("block_length", 30)
        kwargs.setdefault("n_paths", 10000)
        self.bootstrap_results = stationary_block_bootstrap(
            self.log_returns,
            terms_months=self.product_params["available_terms_months"],
            ltv_params=self.product_params,
            **kwargs,
        )

    def _run_blend(self):
        self.blended_results = blend(
            self.backtest_results, self.bootstrap_results,
        )


__all__ = ["LSIEngine"]
