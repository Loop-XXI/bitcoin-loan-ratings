"""BacktestEngine — historical loan liquidation simulation using daily BTC prices.

Slides day-by-day windows for each loan term, tracks LTV against margin-call and
liquidation thresholds under passive and active borrower models.
"""

import csv
import json
import math
import os
import time
import urllib.request
from datetime import datetime, timezone
from statistics import median

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_FILE = os.path.join(DATA_DIR, "btc_daily.csv")
YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD"

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------


def _yahoo_chunk(period1, period2, interval="1d"):
    """Fetch one chunk of BTC-USD daily data from the Yahoo Finance v8 API.

    Parameters
    ----------
    period1 : int
        Start Unix timestamp (seconds).
    period2 : int
        End Unix timestamp (seconds).
    interval : str
        Data granularity (default ``"1d"``).

    Returns
    -------
    dict
        Parsed JSON response.
    """
    url = f"{YAHOO_BASE}?period1={period1}&period2={period2}&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def fetch_btc_data():
    """Fetch BTC daily close prices from the Yahoo Finance v8 API (free, no key
    required), caching results to a local CSV.

    Returns
    -------
    list[(int, float)]
        Sorted (unix_timestamp, price_usd) tuples, one per day.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.isfile(CACHE_FILE):
        print(f"[backtest] Loading BTC data from cache: {CACHE_FILE}")
        prices = []
        with open(CACHE_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prices.append((int(row["timestamp"]), float(row["price"])))
        return prices

    print("[backtest] Fetching BTC daily data from Yahoo Finance …")

    # Yahoo Finance first trade for BTC-USD is 2014-09-17 (1410912000).
    # Request from 2014-01-01 anyway; Yahoo will return data from whenever it
    # has records.
    period1 = 1388534400  # 2014-01-01 00:00:00 UTC
    period2 = int(time.time())

    raw = _yahoo_chunk(period1, period2, interval="1d")
    result = raw["chart"]["result"][0]
    timestamps = result["timestamp"]  # list of int (seconds)
    closes = result["indicators"]["quote"][0]["close"]  # list of float | None

    prices = []
    for ts, close in zip(timestamps, closes):
        if close is not None:
            prices.append((ts, close))

    with open(CACHE_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "date", "price"])
        for ts, px in prices:
            d = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            writer.writerow([ts, d, px])

    print(f"[backtest] Cached {len(prices)} daily prices to {CACHE_FILE}")
    return prices


# ---------------------------------------------------------------------------
# Backtest engine
# ---------------------------------------------------------------------------


class BacktestEngine:
    """Slides day-by-day windows across historical BTC prices and simulates
    loan behaviour for every term in *available_terms_months*.

    Parameters
    ----------
    prices : list[(int, float)]
        Sorted (timestamp, price) tuples.
    """

    def __init__(self, prices):
        self._timestamps = [p[0] for p in prices]
        self._prices = [p[1] for p in prices]

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def simulate(self, product_params, borrower_model="passive"):
        """Run the backtest for every product term.

        Parameters
        ----------
        product_params : dict
            Keys: ``ltv_initial``, ``ltv_margincall``, ``ltv_liquidation``,
            ``grace_window_hours``, ``top_up_permitted``,
            ``available_terms_months`` (list of int).
        borrower_model : str
            ``"passive"`` or ``"active"``.

        Returns
        -------
        dict[int, dict]
            Per-term results::

                {
                    term_months: {
                        "liquidation_count": int,
                        "margin_call_count": int,
                        "total_windows": int,
                        "median_time_to_breach_days": float | None,
                        "worst_window_survived_max_ltv": float | None,
                    },
                    ...
                }
        """
        prices = self._prices
        ltv_i = product_params["ltv_initial"]
        ltv_mc = product_params["ltv_margincall"]
        ltv_liq = product_params["ltv_liquidation"]
        grace_hrs = product_params.get("grace_window_hours", 24)
        top_up = product_params.get("top_up_permitted", False)
        terms = product_params["available_terms_months"]

        grace_days = max(1, math.ceil(grace_hrs / 24))

        results = {}

        for term in terms:
            window_len = term * 30  # days
            n_windows = len(prices) - window_len
            if n_windows <= 0:
                results[term] = {
                    "liquidation_count": 0,
                    "margin_call_count": 0,
                    "total_windows": 0,
                    "median_time_to_breach_days": None,
                    "worst_window_survived_max_ltv": None,
                }
                continue

            liq_count = 0
            mc_count = 0
            days_to_breach = []
            worst_survived_ltv = 0.0

            for start in range(n_windows):
                p0 = prices[start]
                if p0 <= 0:
                    continue

                window_prices = prices[start: start + window_len + 1]

                # state for active model (top-up cycles)
                effective_p0 = p0
                breach_start_day = None
                has_mc = False
                has_liq = False
                first_breach_day = None

                for day_off, pt in enumerate(window_prices):
                    if pt <= 0:
                        continue

                    ltv_t = ltv_i * effective_p0 / pt

                    # margin call check
                    if ltv_t >= ltv_mc and not has_mc:
                        has_mc = True

                    # liquidation check
                    if ltv_t >= ltv_liq:
                        if borrower_model == "passive":
                            if not has_liq:
                                has_liq = True
                                first_breach_day = day_off
                        else:
                            # active borrower model
                            if breach_start_day is None:
                                breach_start_day = day_off

                            elapsed = day_off - breach_start_day

                            if elapsed >= grace_days:
                                if top_up:
                                    # top-up resets effective reference price
                                    # so LTV returns to LTV_initial at this point
                                    effective_p0 = pt * ltv_i / ltv_t
                                    breach_start_day = None
                                else:
                                    if not has_liq:
                                        has_liq = True
                                        first_breach_day = breach_start_day
                    else:
                        # LTV dropped below liquidation threshold
                        if (borrower_model == "active"
                                and breach_start_day is not None):
                            breach_start_day = None  # price recovered

                if has_liq:
                    liq_count += 1
                    if first_breach_day is not None:
                        days_to_breach.append(first_breach_day)

                if has_mc:
                    mc_count += 1

                if not has_liq:
                    max_ltv_w = max(
                        ltv_i * effective_p0 / pt for pt in window_prices if pt > 0
                    )
                    if max_ltv_w > worst_survived_ltv:
                        worst_survived_ltv = max_ltv_w

            med = median(days_to_breach) if days_to_breach else None
            worst = worst_survived_ltv if worst_survived_ltv > ltv_i else None

            results[term] = {
                "liquidation_count": liq_count,
                "margin_call_count": mc_count,
                "total_windows": n_windows,
                "median_time_to_breach_days": med,
                "worst_window_survived_max_ltv": worst,
            }

        return results


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def compute_log_returns(prices):
    """Compute daily log returns from a price sequence.

    Parameters
    ----------
    prices : list[(int, float)]

    Returns
    -------
    list[float]
        ``log(P_t / P_{t-1})`` for each consecutive pair.
    """
    px = [p[1] for p in prices]
    logrets = []
    for i in range(1, len(px)):
        if px[i - 1] > 0 and px[i] > 0:
            logrets.append(math.log(px[i] / px[i - 1]))
    return logrets
