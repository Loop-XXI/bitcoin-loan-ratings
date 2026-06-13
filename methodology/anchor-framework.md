# Anchor Framework — Anchor Grade Methodology

**Version 1.0 | Effective: 2026-01-01**  
**Engine 1 of Project Anchor: Qualitative Structural Safety Rating for Bitcoin-Backed Loans**

---

## Table of Contents

1. [Purpose and Scope](#purpose-and-scope)
2. [Design Principles](#design-principles)
3. [The Five Pillars](#the-five-pillars)
4. [The Composition Function](#the-composition-function)
5. [Evidence-Tier Discounting](#evidence-tier-discounting)
6. [The Five Gates](#the-five-gates)
7. [Grade Bands](#grade-bands)
8. [Gated vs Not Rated](#gated-vs-not-rated)
9. [Disclosure Rules](#disclosure-rules)
10. [Changelog Policy](#changelog-policy)
11. [Relationship to LSI](#relationship-to-lsi)

---

## Purpose and Scope

The Anchor Grade is a **qualitative structural safety rating** for Bitcoin-backed loan products. It evaluates how well a loan product is designed to protect borrowers from avoidable financial harm — structural confiscation, surprise liquidation, custodial failure, opaque terms, and inadequate dispute resolution.

The grade is structural, not predictive. It does **not** forecast default rates, price movements, or lender solvency. It answers one question: *Given the product's published terms, disclosures, and operational evidence, how safely can a reasonably diligent borrower participate?*

Anchor Grades are:

- **Deterministic.** Given the same evidence files, the same grade is always computed.
- **Evidence-based.** Grades derive from published documentation and verifiable operational evidence, not analyst opinion.
- **Borrower-focused.** Every signal is weighted by its impact on borrower outcomes.
- **Transparent.** The full methodology is public. Every sub-score is traced to a specific evidence document.

Anchor Grades are **not**:

- A recommendation to borrow or not borrow.
- An assessment of loan profitability or terms competitiveness.
- A forecast of Bitcoin price or liquidation likelihood.
- Legal or financial advice.

---

## Design Principles

### 1. Weakest-Link Math

The composition function (see §4) uses a **geometric weighted mean**, not an arithmetic sum. This is a deliberate choice: a single failed pillar can dominate the final score no matter how strong the other pillars are. A product with perfect transparency and robust liquidation mechanics but zero recourse for errors receives a failing grade regardless. This mirrors real borrower risk — a single catastrophic failure mode is not offset by excellence elsewhere.

### 2. Evidence Over Claims

Scores are assigned based on what a product **demonstrates**, not what it claims. Each signal is scored against the evidence tier it actually meets (§5). A marketing page that says "borrower-friendly liquidation" without specifying parameters receives the same score as a page that says nothing — zero, until verifiable evidence is produced.

### 3. Unknowns Are Risk

When evidence is absent, the methodology assumes the worst plausible case. This is not punitive; it is conservative by design. A product that has not published its default remediation process is scored as if it has no remediation process, because the borrower has no way to verify otherwise. Products are always free to improve their score by publishing evidence.

### 4. Economics Excluded

The Anchor Grade deliberately excludes:

- Interest rates, fees, and origination costs
- Loan-to-value (LTV) ratios and margin call thresholds
- Bitcoin price forecasts or volatility models
- Lender profitability or business model sustainability

These are evaluated separately by Engine 2 (LSI, §11) and by the borrower's own judgment. The Anchor Grade is purely about **structural safety** — the design choices that protect (or fail to protect) borrowers regardless of market conditions.

---

## The Five Pillars

Each pillar contributes a score between 0 and 100. Pillars are weighted to reflect their relative importance to borrower safety.

| Pillar | Weight | Focus |
|---|---|---|
| P₁ — Custody & Collateral | 25% | Who holds the Bitcoin, under what legal framework, and with what auditability |
| P₂ — Liquidation Mechanics | 25% | How liquidation is triggered, executed, and communicated |
| P₃ — Transparency & Disclosure | 20% | Whether terms are complete, current, and clearly stated |
| P₄ — Recourse & Dispute Resolution | 15% | How errors, disputes, and exceptions are handled |
| P₅ — Operational Resilience | 15% | Platform reliability, contingency planning, and operational history |

### P₁ — Custody & Collateral (25%)

Evaluates the safety and auditability of the collateral custody arrangement.

**Sub-signals:**

1. **Custody structure** — Self-custody (borrower-controlled multi-sig) scores highest. Third-party qualified custodians with bankruptcy remoteness score next. Exchange wallets with no segregation score lowest. Unclear or undisclosed structures score zero.

2. **Legal jurisdiction & framework** — Products operating under a clear regulatory framework (e.g., state lending licenses, UCC Article 9 filings) score higher than those in unregulated or uncertain jurisdictions. Cross-border complexity with no clear governing law is penalized.

3. **Audit trail & proof of reserves** — Regular, third-party proof-of-reserves audits with published reports score highest. Self-reported snapshots score lower. Absence of any auditability scores zero.

4. **Collateral segregation** — Is each borrower's collateral held in a distinct, identifiable wallet or address? Pooled omnibus wallets score lower. Commingled with operational funds scores zero.

5. **Rehypothecation risk** — If terms permit the lender to rehypothecate (re-use, lend, or stake) borrower collateral, the sub-signal is heavily penalized. Explicit prohibition scores highest.

### P₂ — Liquidation Mechanics (25%)

Evaluates how liquidation events are triggered and executed.

**Sub-signals:**

1. **Trigger transparency** — Are the exact LTV thresholds that trigger margin calls and liquidation published? Are they static or dynamic? Products with clearly published, static thresholds score higher than those with opaque or algorithmically undisclosed triggers.

2. **Grace period & cure window** — Is there a defined period between margin call and forced liquidation? Longer windows with clear cure mechanisms score highest. Immediate or same-day liquidation without notification scores zero.

3. **Liquidation execution** — Is liquidation executed via a public, verifiable on-chain mechanism (e.g., DEX swap, auction)? Private off-chain settlement scores lower. Unilateral determination of liquidation price by the lender scores zero.

4. **Liquidation penalty structure** — Are penalties clearly stated, capped, and rationale disclosed? Uncapped or vaguely defined penalties score zero. Penalties that escalate with time (incentivizing early cure) are scored higher than flat penalties.

5. **Partial vs full liquidation** — Does the product liquidate only the minimum necessary to restore a safe LTV, or does it close the entire position? Partial liquidation with borrower notification scores higher.

### P₃ — Transparency & Disclosure (20%)

Evaluates whether a borrower can fully understand the product before committing.

**Sub-signals:**

1. **Terms completeness** — Are all material terms published in a single, current document? Missing terms (e.g., "liquidation fees determined at lender's discretion") reduce the score proportionally to the materiality of the omission.

2. **Plain language** — Is the agreement written in clear, jargon-minimized language suitable for a non-specialist audience? Legal boilerplate with no explanatory summary scores lower. No disclosure at all scores zero.

3. **Historical terms tracking** — Are past versions of terms published and diffable? A changelog or version-controlled terms repository scores highest. Oral or unwritten modifications score zero.

4. **Fee & cost schedule** — Are all fees (origination, servicing, late payment, liquidation, transfer) exhaustively listed with fixed amounts or formulae? Hidden or conditional fees reduce the score.

5. **Jurisdiction & governing law** — Is the governing law and exclusive venue for disputes clearly stated? Ambiguous or absent jurisdiction clauses score zero.

### P₄ — Recourse & Dispute Resolution (15%)

Evaluates what a borrower can do when something goes wrong.

**Sub-signals:**

1. **Dispute mechanism** — Is there a published, actionable dispute resolution process? Independent arbitration (with borrower input on arbitrator selection) scores highest. "Contact support" with no escalation path scores low. No published process scores zero.

2. **Error correction** — Does the product have a defined process for correcting operational errors (over-liquidation, miscalculated interest, lost transactions)? Defined SLA with remedy scores highest. No policy scores zero.

3. **Cure rights** — Can a borrower cure a margin call by adding collateral, making a partial payment, or both? Products offering multiple cure paths score higher than single-path or no-cure products.

4. **Force majeure & exception handling** — Are catastrophic scenarios (fork, hack, chain reorganization) addressed in the terms? Blanket force majeure clauses that waive all lender obligations score zero. Specific, bounded exceptions with borrower protections score higher.

### P₅ — Operational Resilience (15%)

Evaluates the platform's ability to function reliably.

**Sub-signals:**

1. **Platform uptime & SLA** — Is there a published uptime SLA? Are historical outages documented? No SLA scores zero.

2. **Redundancy & continuity** — Is the platform designed with infrastructure redundancy? Are there documented business continuity and disaster recovery plans? Undisclosed scores zero.

3. **Operational history** — Years of continuous operation, audit history, and regulatory standing contribute positively. New platforms with no track record score baseline (not zero — lack of history is not a penalty, but no evidence scores zero on the other sub-signals).

4. **Security posture** — Have there been published security audits? Is there a bug bounty program? Has the platform suffered security incidents, and if so, how were they disclosed and remediated?

---

## The Composition Function

### Formula

```
AnchorScore = 100 × ∏_{i=1}^{5} ( max(P_i, 1) / 100 )^{w_i}
```

Where:

- `P_i` is the raw pillar score (0–100) after evidence-tier discounting
- `w_i` is the pillar weight (P₁=0.25, P₂=0.25, P₃=0.20, P₄=0.15, P₅=0.15)
- `max(P_i, 1)` ensures no pillar contributes zero to the product (see below)
- The result is scaled to a 0–100 numeric score

### Why Geometric Mean?

The geometric weighted mean is the **defining architectural choice** of the Anchor Framework. It implements weakest-link logic directly in the mathematics, without penalty tables or ad-hoc conditionals.

**Arithmetic mean behavior** (what we deliberately avoid):

- A product scoring 90, 90, 90, 10, 90 would average 74 — a passing grade despite a catastrophic failure in one area.
- This masks risk. A borrower does not care that four pillars are excellent when the fifth means their collateral can be liquidated without notice.

**Geometric mean behavior** (what we use):

- A product scoring 90, 90, 90, 10, 90 yields approximately 47 — a failing grade, because one critical pillar is near zero.
- As any single pillar approaches zero, the entire product approaches zero, regardless of other scores.
- This is not a bug or a "tough penalty." It faithfully represents the borrower's experience: a single catastrophic failure mode is not compensated by unrelated strengths.

### The Floor of 1

We use `max(P_i, 1)` rather than allowing a true zero in the product. This is **not** a loophole — a pillar score of 1 still contributes a factor near zero (`(1/100)^w_i`). The floor exists solely to prevent the degenerate mathematical case where a single score of exactly 0.0 would make the entire product exactly 0, masking the relative contributions of other pillars. A score of 1 is still a failing pillar and produces a failing overall grade.

### Weight Rationale

Custody and Liquidation Mechanics are weighted highest (25% each) because failure in either can result in **immediate, total loss** of borrower collateral. Transparency (20%) is the enabling condition — without it, borrowers cannot assess any other pillar. Recourse and Operational Resilience (15% each) are important but are downstream mitigations rather than primary failure modes.

---

## Evidence-Tier Discounting

Each sub-signal is scored at one of five evidence tiers. The tier determines the maximum assignable score for that sub-signal.

| Tier | Label | Description | Max Score |
|---|---|---|---|
| E₅ | Published & Verified | Terms evidenced in a current, publicly accessible document, confirmed by independent third-party verification (audit, regulatory filing, qualified custodian attestation) | 100 |
| E₄ | Published & Self-Attested | Terms evidenced in a current, publicly accessible document, attested by the product's own statements without independent verification | 75 |
| E₃ | Published, Outdated | Terms evidenced in a publicly accessible document but the document is dated or known to be superseded | 50 |
| E₂ | Referenced but Not Published | Terms referenced in marketing materials, blog posts, or support communications without a canonical document | 25 |
| E₁ | Absent or Vague | No specific evidence; generic claims without operational detail; "we prioritize borrower safety" with no supporting documentation | 0 |

### How Discounting Works

Each sub-signal score is computed as:

```
sub_score = tier_max_score × evidence_quality_factor
```

Where `evidence_quality_factor` ∈ [0.0, 1.0] captures how well the evidence satisfies the sub-signal's specific criteria at that tier. For example, a product that publishes a complete liquidation policy (E₄, max 75) that is clear, specific, and covers all sub-signal criteria might receive a quality factor of 1.0 (score 75). A product that publishes a policy with gaps or ambiguous language might receive 0.6 (score 45).

### Rationale

Evidence-tier discounting ensures that **the grade reflects what borrowers can actually know**, not what the product claims internally. A product with an excellent but unpublished liquidation policy is functionally identical to a product with no policy at all — in both cases, the borrower cannot verify protection before committing collateral.

---

## The Five Gates

Before final grade assignment, each product passes through five **gates** — binary pass/fail checks that test for non-negotiable structural requirements. If any gate is failed, the product is marked **Gated** and receives no numeric grade.

| Gate | Criteria |
|---|---|
| **G₁ — Identity** | The product must identify a legal operating entity (corporate name, jurisdiction of incorporation, and registered address). Anonymous or pseudonymous products without a verifiable legal identity fail. |
| **G₂ — Terms of Service** | A publicly accessible, current terms-of-service or loan agreement must exist. Products that require account creation or NDA to view terms fail. |
| **G₃ — Liquidation Disclosure** | The terms must disclose the basic liquidation mechanism (triggers, penalties, execution method). Products that do not disclose how liquidation works at all fail. |
| **G₄ — Jurisdiction** | The terms must specify a governing law and exclusive jurisdiction (or binding arbitration venue). Products with no governing law clause fail. |
| **G₅ — Solvency & Availability** | The product must be currently accepting new borrowers (or have done so within the past 90 days). Discontinued, pre-launch, or permanently closed products fail. |

### Gate Failure vs Low Score

A gate failure means "this product cannot be rated in its current state." It is distinct from a low pillar score, which means "this product is rated and scored poorly." A product that fails G₂ (no public terms) receives no grade regardless of its custody or liquidation quality — because without public terms, no pillar can be assessed reliably.

---

## Grade Bands

| Numeric Range | Letter Grade | Label | Meaning |
|---|---|---|---|
| 85–100 | AAA | Excellent | Structural safety is robust across all pillars. Weakest-link analysis shows no critical gaps. |
| 70–84 | AA | Good | Strong structural safety with minor gaps that do not threaten borrower outcomes in normal circumstances. |
| 55–69 | A | Adequate | Acceptable structural safety but with identifiable gaps that could affect borrower outcomes in stressed conditions. |
| 40–54 | BBB | Below Adequate | Structural safety has multiple gaps. Borrower should exercise caution and conduct independent due diligence beyond the Anchor Grade. |
| 25–39 | BB | Weak | Significant structural safety gaps. Borrower should assume elevated risk of adverse outcomes. |
| 10–24 | B | Poor | Critical structural safety gaps. Borrower should expect that one or more failure modes could result in total collateral loss. |
| 0–9 | C | Failing | Structural safety is fundamentally absent. Borrower should not participate. |
| — | Gated | Gated | One or more gate criteria are not met. Product cannot be rated until gates are satisfied. |
| — | NR | Not Rated | Product has not been evaluated under this methodology. |

### Grade Stability

Grades are **not** normally distributed or forced onto a curve. It is possible (and expected) that all rated products fall into a narrow band, or that no product achieves AAA. The grade reflects absolute structural quality, not relative ranking.

---

## Gated vs Not Rated

| Status | Meaning |
|---|---|
| **Gated** | The product was evaluated but failed one or more gates. No numeric grade is assigned. The specific gates failed are documented. |
| **NR (Not Rated)** | The product has not been evaluated. This may be because the product declined to participate, insufficient evidence was available to begin evaluation, or evaluation is in progress. |

Products that are Gated can become rateable by remediating the failed gate(s). Products that are NR can become rateable by providing sufficient evidence for evaluation.

---

## Disclosure Rules

### Required Disclosures

Every published grade must be accompanied by:

1. **The date** of the most recent evaluation
2. **The evidence files** used (linked or referenced)
3. **The pillar scores** (P₁–P₅) and the overall AnchorScore
4. **The evidence tier** achieved for each sub-signal
5. **A changelog** reference showing what changed from the prior grade (if applicable)

### Not-Advice Language

The following disclaimer must accompany every published grade:

> **Anchor Grades are structural safety assessments only. They do not constitute financial, legal, or investment advice. An Anchor Grade is not a recommendation to borrow, lend, or refrain from either. Past grades do not guarantee future grades. No grade guarantees against loss of collateral, including total loss. Each borrower should conduct their own due diligence and consult qualified professionals before entering any loan agreement.**

### Restrictions

- Anchor Grades may not be used in lender marketing materials without including the full grade report (not just the letter grade).
- Anchor Grades may not be cherry-picked (e.g., citing only the letter grade without the accompanying pillar scores and disclaimers).
- Anchor Grades may not be represented as endorsements by Project Anchor, Loop LLC, or any affiliated entity.

---

## Changelog Policy

### Scheduled Updates

Grades are recomputed at least once per calendar quarter. The quarterly review cycle includes:

- Re-examination of all evidence files for each product
- Verification that links and references are still current
- Re-scoring against the current methodology version

Quarterly review dates are published in advance. Products are notified prior to review.

### Event-Driven Updates

Grades may be updated between scheduled reviews when:

- A product publishes revised terms, disclosures, or operational documentation
- A product experiences a publicly reported security incident, regulatory action, or operational failure
- A change in the product's legal structure, jurisdiction, or custody arrangement is announced
- New evidence becomes available that materially affects a pillar score
- The methodology itself is revised (see versioning below)

Event-driven updates are published within 10 business days of the triggering event becoming known to the rating team.

### Methodology Versioning

The methodology is versioned (see header). Major versions (e.g., 2.0) indicate changes that alter the computation or grading scale. Minor versions (e.g., 1.1) indicate clarifications, corrections, or expanded guidance without changing the underlying computation.

All prior methodology versions are archived and publicly accessible. Grades are always computed against the current methodology version. Historical grades are recomputed against the methodology version that was current at the time of the grade (not retroactively updated to new methodology unless a major version explicitly includes a re-rating directive).

---

## Relationship to LSI

The Anchor Grade is one of two evaluation engines in Project Anchor. The other is the **Liquidation Stress Index (LSI)** .

| Dimension | Anchor Grade (Engine 1) | LSI (Engine 2) |
|---|---|---|
| **What it measures** | Qualitative structural safety | Quantitative liquidation risk |
| **Input** | Published terms, evidence files, operational documentation | Loan parameters (LTV, term, margin call thresholds, fees) |
| **Method** | Structured rubric with evidence-tier discounting + geometric composition | Historical backtest + bootstrap Monte Carlo simulation |
| **Output** | Letter grade (AAA–C) plus numeric AnchorScore | Numeric probability (0.00–1.00) with stress bands |
| **Temporality** | Point-in-time, updated quarterly or event-driven | Rolling, recomputed weekly |
| **What it captures** | Design choices, disclosure quality, recourse options | Historical BTC price behavior and its impact on loan positions |
| **What it excludes** | Price, rates, liquidation probability | Structural terms, transparency, recourse |

The two engines are designed to be complementary. A product may have a strong Anchor Grade (well-designed terms, transparent disclosure) but a weak LSI (aggressive LTV in a volatile market), or vice versa. **Neither engine alone provides a complete assessment.** Project Anchor recommends that borrowers consider both before making a decision.

---

*This methodology is maintained by Loop LLC / LedgerRatings. Questions, corrections, and evidence submissions should be directed to methodology@ledgerratings.com.*
