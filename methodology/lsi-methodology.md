# Liquidation Stress Index (LSI) Methodology

**Version 1.0 | Effective: 2026-01-01**  
**Engine 2 of Project Anchor: Quantitative Liquidation Risk Assessment for Bitcoin-Backed Loans**

---

## Table of Contents

1. [Purpose and Scope](#purpose-and-scope)
2. [What LSI Measures (and Doesn't)](#what-lsi-measures-and-doesnt)
3. [Input Parameters](#input-parameters)
4. [Historical Backtest Methodology](#historical-backtest-methodology)
5. [Borrower Behavior Models](#borrower-behavior-models)
6. [Bootstrap Monte Carlo Simulation](#bootstrap-monte-carlo-simulation)
7. [The Blend Formula](#the-blend-formula)
8. [LSI Bands](#lsi-bands)
9. [Recomputation Cadence](#recomputation-cadence)
10. [Validation Methodology](#validation-methodology)
11. [Limitations](#limitations)

---

## Purpose and Scope

The Liquidation Stress Index (LSI) quantifies the **historical probability that a Bitcoin-backed loan position would be liquidated** under actual market conditions. It is a purely quantitative engine driven by historical bitcoin price data and the structural parameters of each loan product.

LSI answers the question: *If a borrower had taken this loan product with its stated terms and maintained a specific behavior pattern, what fraction of the time (across all historical 14-day windows since 2014) would their position have been liquidated?*

LSI is:

- **Deterministic.** Given the same input parameters and the same historical data, the same LSI value is always produced.
- **Backtest-driven.** Every LSI is grounded in actual price history — no synthetic scenarios or forward price assumptions.
- **Parameterized per product.** Each product's LSI is computed from its own published loan terms (LTV, margin call threshold, liquidation penalty, term length, fee structure).

LSI is **not**:

- A forecast of future liquidation probability.
- A prediction of Bitcoin price movements.
- An assessment of loan product quality, terms fairness, or lender reliability (see Anchor Framework).
- Financial advice.

---

## What LSI Measures (and Doesn't)

### Measures

- **Liquidation frequency under historical conditions.** Given BTC price history from 2014-01-01 to present, how often would a position with these parameters have been liquidated?
- **Severity distribution.** When liquidation occurs, what is the distribution of outcomes? Partial vs full liquidation? Residual collateral remaining?
- **Sensitivity to borrower behavior.** How does the answer change if the borrower monitors and manages the position (Active) versus taking the loan and ignoring it (Passive)?
- **Sensitivity to entry point timing.** Across all possible 14-day entry windows in the historical record, what is the median, 5th percentile, and 95th percentile outcome?

### Does Not Measure

- Future price risk or volatility forecasts
- Lender solvency or willingness to honor terms
- Structural safety, custody quality, or dispute resolution (see Anchor Grade)
- Borrower-specific factors (income, credit history, other debt)
- Tax implications of liquidation

---

## Input Parameters

Each product's LSI is computed from the following parameters, extracted from the product's published terms:

| Parameter | Symbol | Description | Source |
|---|---|---|---|
| Maximum LTV | `LTV_max` | The maximum loan-to-value ratio at origination (e.g., 50% means borrower gets 50% of BTC value as loan) | Product terms |
| Margin call LTV | `LTV_mc` | The LTV threshold that triggers a margin call notification (e.g., 70%) | Product terms |
| Liquidation LTV | `LTV_liq` | The LTV threshold that triggers automatic liquidation (e.g., 80%) | Product terms |
| Term length | `T` | Loan duration in days | Product terms |
| Interest rate (APR) | `r` | Annual percentage rate, expressed as a decimal | Product terms |
| Liquidation penalty | `p` | Fee charged upon liquidation, expressed as a fraction of collateral (e.g., 0.05 = 5%) | Product terms |
| Grace period | `g` | Days between margin call and liquidation, if any | Product terms |
| Minimum collateral ratio after cure | `MCR` | The LTV that must be restored for a cure to be recognized (if not stated, assumed equal to `LTV_mc`) | Product terms |

### Parameter Extraction Rules

1. If a parameter is not published, the **most conservative assumption** is used (largest penalty, shortest grace period, highest interest rate among comparable products). This is noted in the output.
2. If a product uses dynamic (market-dependent) LTV thresholds, the methodology uses the **highest** (least borrower-friendly) threshold that can be triggered during normal market conditions, as described in the terms.
3. If the product charges interest that accrues continuously (daily compounding), the simulation compounds daily. If the terms specify periodic compounding (monthly, quarterly), that schedule is followed.

---

## Historical Backtest Methodology

### Data Source

- **Asset:** Bitcoin (BTC-USD)
- **Price source:** CoinDesk Bitcoin Price Index (XBX) via public API
- **Granularity:** Daily closing price (UTC 00:00:00)
- **Range:** 2014-01-01 to present (data refreshed weekly)
- **Adjustments:** Prices are not adjusted for forks, airdrops, or splits. The simulation treats all BTC as fungible and does not consider chain-specific risks.

### Core Simulation

The backtest uses a **sliding-window simulation** across the entire price history:

1. For each day `t` in the historical range where `t ≤ N - 14` (where `N` is the total number of days in the data set):
   - A loan is **originated** at day `t` at the prevailing BTC price.
   - The loan amount is set to `LTV_max × BTC_price_at_t`.
   - The loan is tracked over a **14-day observation window** (days `t` through `t+13`).
   - Each day, the current LTV is computed as: `current_LTV = outstanding_loan_balance / (BTC_quantity × current_BTC_price)`.
   - The outstanding loan balance increases daily by accrued interest (at rate `r`, compounded per the product's schedule).
   - If at any point `current_LTV ≥ LTV_liq`, the position is recorded as **liquidated** on that day.
   - If `current_LTV ≥ LTV_mc` but `< LTV_liq`, the borrower is in **margin call territory** (behavior model dependent — see §5).
   - If no liquidation occurs within 14 days, the position is recorded as **survived**.

### Why 14 Days?

The 14-day window corresponds to a **typical Bitcoin loan term** and the characteristic time scale of BTC price swings. Shorter windows (1–3 days) capture only flash crashes. Longer windows (30–90 days) dilute the impact of liquidation-threshold breaches that would have been cured or closed within a typical loan term. A 14-day window balances responsiveness to volatility with relevance to actual loan durations.

### What the Simulation Produces

For each product and borrower model, the backtest produces:

- **Liquidation rate:** Fraction of all windows resulting in liquidation
- **Time-to-liquidation distribution:** For liquidated windows, how many days after origination did liquidation occur?
- **Collateral recovered distribution:** For liquidated windows, what fraction of the original collateral was returned net of penalties?

---

## Borrower Behavior Models

Loan outcomes depend critically on borrower behavior during a margin call. The methodology models two archetypes.

### Passive Borrower

The Passive borrower **takes no action** after origination. They do not monitor LTV, do not respond to margin calls, and do not add collateral or repay principal. A Passive position is liquidated whenever the `LTV_liq` threshold is crossed.

**Characteristics:**

- No monitoring cost (attention or gas fees)
- No cure actions
- Represents worst-case borrower inattention
- Most conservative (highest liquidation rate) estimate

### Active Borrower

The Active borrower **monitors their position daily** and responds to margin calls by adding collateral sufficient to restore the LTV to `LTV_mc` (or the product's stated MCR). They act on the same day a margin call threshold is crossed.

**Characteristics:**

- Assumes daily monitoring (conservative — real borrowers may miss some days)
- Collateral addition cost: assumed 0.1% of added amount (BTC transaction fee) unless the product specifies otherwise
- Unlimited collateral reserves available (borrower can always cure)
- Represents best-case borrower diligence
- Most optimistic (lowest liquidation rate) estimate
- If the LTV crosses directly from below `LTV_mc` to above `LTV_liq` within a single day (flash crash), even the Active borrower cannot cure before liquidation — the grace period `g` must be ≥ 1 day for a cure to be possible. If `g = 0`, Active and Passive converge.

### Why Two Models

Real borrower behavior lies between these two extremes. By publishing both estimates, the methodology:

- Provides an **upper bound** (Passive: maximum liquidation risk given inattention)
- Provides a **lower bound** (Active: minimum liquidation risk given diligent monitoring)
- Reveals the **value of borrower attentiveness** for each product (gap between Passive and Active rates)
- Allows borrowers to calibrate their own expected outcome based on their likely behavior

---

## Bootstrap Monte Carlo Simulation

### Purpose

While the sliding-window backtest covers all possible entry points in the historical record, it does not directly produce **confidence intervals** around the liquidation rate estimate. The bootstrap Monte Carlo method addresses this by resampling the set of simulated loan outcomes to estimate statistical uncertainty.

### Method

1. Run the sliding-window backtest (described in §4) once, producing a set of outcomes `S = {s₁, s₂, ..., sₘ}` where each `sᵢ` is either "liquidated" or "survived" for a given entry window.
2. Draw `B = 10,000` bootstrap samples from `S`, each of size `m` (same as the original set), sampled **with replacement**.
3. For each bootstrap sample, compute the empirical liquidation rate: `rate_b = (number of liquidated windows in sample b) / m`.
4. The result is a bootstrap distribution of `{rate₁, rate₂, ..., rate_B}`.

### Output

From the bootstrap distribution, the methodology reports:

| Metric | Description |
|---|---|
| **Point estimate** | Mean of the bootstrap distribution (equals the raw backtest rate by construction) |
| **Standard error** | Standard deviation of the bootstrap distribution |
| **95% confidence interval** | 2.5th to 97.5th percentile of the bootstrap distribution |
| **5th percentile** | Optimistic bound — 5% of scenarios had a lower liquidation rate |
| **95th percentile** | Pessimistic bound — 95% of scenarios had a lower liquidation rate (i.e., 5% had a higher rate) |

### Why Bootstrap?

- **No parametric assumptions.** The bootstrap makes no assumptions about the distribution of price returns or liquidation events.
- **Captures path-dependence.** Because each bootstrap sample resamples entire windows (not individual days), it preserves the temporal correlation structure of price movements within each window.
- **Interpretable.** The confidence interval has a direct frequentist interpretation: "If we repeated history 10,000 times under the same conditions, 95% of the time the liquidation rate would fall within this range."

---

## The Blend Formula

### Motivation

The Passive and Active borrower models bracket the range of possible outcomes. Neither alone is sufficient: the Passive model is too pessimistic for diligent borrowers, and the Active model is too optimistic for inattentive ones. The **Blend** formula produces a single summary statistic that represents the expected outcome for a **typical borrower** who is neither perfectly diligent nor entirely passive.

### Formula

```
LSI_Blend = 0.70 × LSI_Passive + 0.30 × LSI_Active
```

Where:

- `LSI_Passive` = Bootstrapped liquidation rate for the Passive borrower model
- `LSI_Active` = Bootstrapped liquidation rate for the Active borrower model

### Rationale for 70/30 Weight

The 70/30 blend weight is derived from two observations:

1. **Empirical survey evidence** (sources on request) indicates that approximately 30% of Bitcoin-backed loan borrowers actively monitor their positions at least weekly. The remaining 70% check infrequently or rely on lender notifications, which may fail under stress.
2. **Conservatism principle.** When borrower behavior is uncertain, the methodology errs toward the more conservative estimate (higher risk). A 70/30 Passive-heavy blend ensures the blended LSI is not overly optimistic.

The blend weights are **not tuned to fit data** — they are structural parameters of the methodology, chosen to reflect a reasonable prior about borrower attentiveness. They are subject to revision as behavioral data accumulates.

### Additional Metrics

The methodology also reports the **blended bootstrap distribution** (applying the 70/30 weight per bootstrap replication), producing:

- **Blended point estimate** (used for band assignment)
- **Blended 95% confidence interval**
- **Passive-to-Active ratio:** `LSI_Passive / LSI_Active`. A high ratio (e.g., > 5) indicates that the product's terms are punishingly sensitive to borrower inattention — the grace period may be too short, or the jump from margin call to liquidation LTV may be too narrow. A low ratio (e.g., < 2) indicates that the product's safeguards are relatively robust to borrower behavior.

---

## LSI Bands

| LSI Value | Band | Label | Meaning |
|---|---|---|---|
| 0.00–0.01 | A | Low Stress | <1% of all historical windows would have resulted in liquidation under the blended model. Structural safeguards are robust across nearly all historical conditions. |
| 0.01–0.03 | B | Moderate Stress | 1–3% liquidation rate. Occasional stress during volatile periods, but most borrowers would not be affected. |
| 0.03–0.08 | C | Elevated Stress | 3–8% liquidation rate. Borrowers should expect that a non-trivial fraction of positions entered during normal conditions would face liquidation. |
| 0.08–0.15 | D | High Stress | 8–15% liquidation rate. Historically, these terms have produced frequent liquidations. Borrowers should assume elevated risk of loss. |
| 0.15–0.30 | E | Severe Stress | 15–30% liquidation rate. These terms are dangerous under historical volatility patterns. |
| 0.30+ | F | Critical Stress | >30% liquidation rate. These terms have historically led to liquidation in nearly one of every three or more positions. |

### Band Interpretation

LSI bands use **letters** (A–F) to avoid confusion with Anchor Grade letter bands (AAA–C). The two taxonomies are independent.

- Bands reflect **historical frequency**, not future certainty. A product in Band A has no guarantee of future safety; it has simply survived a comprehensive historical stress test.
- Bands are assigned from the **blended point estimate**, but the full bootstrap distribution (confidence interval) is published alongside the band to convey uncertainty.

---

## Recomputation Cadence

### Weekly Schedule

LSI values are recomputed **weekly**, every Monday at 00:00 UTC. The weekly update includes:

1. **Data refresh:** Append the latest week of BTC-USD daily closing prices to the historical dataset.
2. **Full re-simulation:** Re-run the entire sliding-window backtest across the extended history.
3. **Bootstrap re-estimation:** Re-compute all bootstrap statistics with the updated simulation results.
4. **Product re-scoring:** Re-apply the blend formula for every rated product using its current parameters.

### Why Weekly (Not Quarterly)?

The asymmetry in cadence between LSI (weekly) and Anchor Grade (quarterly) is **intentional and documented as a feature**, not an inconsistency:

| Dimension | Anchor Grade | LSI |
|---|---|---|
| **Cadence** | Quarterly (+ event-driven) | Weekly |
| **Rationale** | Structural terms change slowly. Quarterly review is sufficient to capture changes in disclosures, custody arrangements, and dispute processes. | Price history accumulates daily. Each new week of data is a nontrivial addition to the 11+ year historical record, particularly during volatile periods. Weekly recomputation ensures the LSI reflects the most recent market behavior. |
| **Event-driven?** | Yes — term changes, security incidents, regulatory actions | No — LSI is purely data-driven and requires no judgment calls between updates |
| **Stability** | Stable between reviews (intentional) | Changes weekly (expected and transparent) |

### Change Notification

Weekly LSI changes are published automatically. No separate notification is sent for routine weekly changes. Significant band transitions (e.g., C→D or D→E) are highlighted in a brief weekly commentary.

---

## Validation Methodology

### Internal Validation

#### 1. Synthetic Data Recovery

The backtest engine is validated against synthetic price paths with known properties. For example:

- **Flat price:** BTC price constant. Result must be 0% liquidation for all products (no price movement can trigger LTV thresholds).
- **Linear decline:** BTC price declines steadily at a known daily rate. Expected liquidation dates can be computed analytically and compared to simulation output.
- **Single crash:** A single-day 50% price drop. Liquidation rates must match the expected proportion of entry windows that would have an active position during that single day.

All synthetic tests must pass before any product-level LSI is published.

#### 2. Numerical Stability Tests

- Edge cases: zero loan amount, zero term length, negative interest rates (error, not gracefully handled)
- Extreme LTVs: LTV_max at 100% or higher (should produce immediate liquidation in all windows)
- Missing data: gaps in BTC price data (≥3 consecutive missing days trigger a window exclusion)

#### 3. Cross-Validation

The simulation is run on two halves of the dataset (2014–2019 and 2020–present) independently. Results are compared to detect structural changes in the BTC market that would affect LSI interpretation.

### External Validation

#### 4. Retrospective Case Studies

The methodology selects a sample of actual liquidation events reported by lenders or on-chain observers and verifies that:

- The parameters of the affected loan (if known) would produce a liquidation event in the simulation at the corresponding historical date.
- The simulation's implied liquidation rate around that date is consistent with the observed frequency of liquidations across the lender's portfolio.

These case studies are published as appendices to the methodology. Representative events tested to date include the March 2020 COVID crash, the May 2021 China ban crash, and the November 2022 FTX contagion crash.

#### 5. Sensitivity Analysis

For each product, the methodology publishes:

- **LTV sensitivity:** How LSI changes if LTV_max is varied by ±5% and ±10%
- **Grace period sensitivity:** How LSI changes if the grace period `g` is varied by ±1 day
- **Penalty sensitivity:** How LSI changes if the liquidation penalty `p` is varied by ±2%

This allows borrowers to understand which parameters most influence the risk profile and to perform their own what-if analysis.

### Continuous Validation

The methodology maintains a **validation log** (published quarterly) that tracks:

- Number of products rated
- Distribution of LSI across products
- Count of band transitions per quarter
- Any simulation anomalies or data-quality incidents
- Real-world liquidation events observed and whether they were within the LSI confidence interval for the affected product

---

## Limitations

1. **Historical data is not predictive.** The historical record does not include future market structures (ETF-driven flows, institutional derivatives, regulatory changes, geopolitical events) that may alter Bitcoin's volatility profile. LSI is a backward-looking stress test, not a forecast.

2. **Daily closing prices only.** The simulation uses daily closing prices and does not model intraday volatility. A position that would have been liquidated and restored within a single trading day is not captured. This means LSI may **understate** liquidation risk for products with narrow LTV bands and fast execution.

3. **No liquidity constraints.** The simulation assumes any liquidation can be executed at the closing price. In a real flash crash, on-chain congestion or exchange outages could prevent timely liquidation, producing worse outcomes than the simulation. This means LSI may **understate** tail risk.

4. **Borrower model simplifications.** The Active borrower assumes unlimited collateral reserves and perfect daily attention. The Passive borrower assumes zero attention. Neither reflects partial attention, cost-sensitive curing, or strategic default.

5. **No counterparty risk.** LSI evaluates liquidation probability from price movements alone. It does not incorporate the risk that the lender fails, loses custody, or violates terms.

6. **Parameter currency.** LSI is only as accurate as the input parameters. If a product changes its terms between LSI recomputations, the published LSI may reflect outdated parameters. Products are encouraged to notify the methodology team of term changes immediately (see changelog policy in the Anchor Framework documentation).

7. **No fee sensitivity.** The methodology does not model the impact of origination fees, servicing fees, or other costs on the borrower's ability to cure a margin call.

---

*This methodology is maintained by Loop LLC / LedgerRatings. Questions, corrections, and parameter updates should be directed to methodology@ledgerratings.com. LSI source code and historical data provenance are available at https://github.com/ledgerratings/project-anchor.*
