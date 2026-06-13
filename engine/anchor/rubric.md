# Anchor Grade — Complete Sub-Signal Rubrics

Each sub-signal is scored on a 0–100 scale with **five anchor points**:
**0**, **25**, **50**, **75**, and **100**.  Analysts interpolate between
anchor points as appropriate.

---

## Pillar 1 — Key Control & Exit (weight 0.28)

### 1a_arch — Unilateral Exit: Architecture (verifiable from code/on-chain)
Can the borrower technically recover collateral without the operator's participation, based on the system's architecture?

| Score | Anchor |
|-------|--------|
| 0 | **Single-key architecture** — operator controls all keys. No technical path for borrower to recover without operator. |
| 25 | **Shared custody with operator veto** — borrower holds a key, but the quorum requires operator's signature to move coins (e.g., 2-of-3 where operator controls 2 keys). |
| 50 | **Partial independence** — borrower + one independent party can sign without operator, but the independent party is nominated/controlled by the operator (e.g., 2-of-3 multisig where a Key Agent is appointed by the provider). |
| 75 | **Borrower + independent party can exit without operator** — 2-of-3 where borrower + an independent third party (not operator-affiliated) can sign. Recovery tooling is documented and available. |
| 100 | **Fully script-enforced unilateral recovery** — borrower holds all keys needed for exit. No counterparty of any kind needed (e.g., on-chain covenant, taproot script path, time-locked refund in a self-custodial protocol). |

> **Evidence tiering note:** Score is based on what the code and on-chain data prove, not what marketing claims. Open-source multisig coordination software (e.g., Caravan) is T1-verifiable. The actual multisig address structure is T1-verifiable on-chain.

---

### 1a_contract — Unilateral Exit: Contractual Right (mid-loan/provider dependence)
Does the written agreement allow the borrower to exit mid-loan without the provider's active cooperation?

| Score | Anchor |
|-------|--------|
| 0 | **No contractual right to exit** — collateral is held for the full term with no early release mechanism. |
| 25 | **Contractual right exists** but enforcement requires provider's active cooperation (e.g., provider must process payoff, sign release tx, or approve surrender). No script-enforced or pre-signed mechanism. |
| 50 | **Contractual right with conditional automation** — provider cooperation is required but the conditions and process are fully documented and binding (e.g., "pay off balance → collateral released within X business days"). |
| 75 | **Pre-signed or timelocked exit mechanism** — borrower holds a pre-signed refund transaction or timelock that releases collateral upon meeting contractual conditions (e.g., paying off loan). Provider cannot refuse. |
| 100 | **Fully script-enforced unilateral exit mid-loan** — borrower can reclaim collateral at any time via an on-chain mechanism without any counterparty action, even while the loan is active. Contract is self-executing. |

> CeFi products with pure custodial control score ≤25 here: no on-chain mechanism, full provider dependence for exit.

---

### 1b — Quorum Architecture
Distribution, independence, and redundancy of key-holding parties.

| Score | Anchor |
|-------|--------|
| 0 | **Single key** held by one party (operator only). |
| 25 | **Threshold of 2** keys but both controlled by operator or related entities (no independence). |
| 50 | **m-of-n with m ≥ 2**, all key holders are independent entities, but geographic / legal redundancy is limited. |
| 75 | **m-of-n with m ≥ 3**, geographically diverse, legally independent key holders. At least one key held by borrower or borrower-nominated party. |
| 100 | **m-of-n with m ≥ 3, n ≥ 5**, fully independent entities across multiple jurisdictions, with borrower-controlled key AND a dispute-resolution fallback (e.g., emergency timelock council). |

---

### 1c — Failure Recovery
Documented path for collateral recovery if the platform or operator disappears.

| Score | Anchor |
|-------|--------|
| 0 | **No documented recovery plan.** If the operator ceases operations, collateral is presumed lost. |
| 25 | **Vague assurances** of recovery but no binding or auditable process (e.g., "we will try to return funds"). |
| 50 | **Written recovery plan** exists, but depends on operator's continued cooperation or goodwill of a single entity. No script-enforced fallback. |
| 75 | **Recovery plan published and verifiable**, involving multiple independent parties (e.g., inheritance clause in smart contract, backup key holders with legal obligations). Manual intervention still required but path is clear. |
| 100 | **Script-enforced automatic recovery** — collateral is returned to borrower automatically if the operator fails to perform within a defined window (e.g., automated refund covenant, deadline-n履约 mechanism). No human cooperation needed. |

---

### 1d — Legal Claim Quality
Strength of the borrower's legal claim to their collateral.

| Score | Anchor |
|-------|--------|
| 0 | Borrower is an **unsecured creditor** with no special claim to the specific collateral assets. Collateral is on operator's balance sheet. |
| 25 | Borrower has a **contractual claim** to return of collateral, but it is not bankruptcy-remote. In a bankruptcy proceeding, borrower ranks with general unsecured creditors. |
| 50 | Collateral is **legally segregated** (not on operator's balance sheet) but borrowers are still subject to stay or clawback in bankruptcy. Trust or SPV structure, but not fully proven. |
| 75 | Collateral is held in a **bankruptcy-remote SPV or trust** with clear beneficial ownership for the borrower. Legal opinions support borrower's claim *not* being estate property. |
| 100 | Collateral is **provably non-custodial or on-chain self-custodial** — bankruptcy of operator cannot affect borrower's possession of the assets. Legal claim is redundant because enforcement is via script/code. |

---

## Pillar 2 — Asset Fidelity (weight 0.22)

### 2a — Collateral Form
What form does the collateral asset take?

| Score | Anchor |
|-------|--------|
| 0 | **Paper claim / IOU** — no on-chain representation. Collateral is a purely off-chain ledger entry. |
| 25 | **Lightly-audited bridge** — wrapped or bridged BTC with limited audit transparency and no proven finality guarantees. |
| 50 | **Wrapped BTC** (e.g., WBTC, tBTC on Ethereum) — centralized or federated custodian, but token is widely verified. Borrower depends on bridge operator. |
| 75 | **Federated peg** (e.g., RSK, Liquid) — BTC is locked in a federated multisig and a sidechain token is minted. Federation provides verifiable peg-in/out. |
| 100 | **Native on-chain BTC** — collateral is held as actual Bitcoin UTXOs on the Bitcoin base layer. No wrapping, no pegging, no bridges. |

---

### 2b — Reuse Rights
Can the collateral be reused (rehypothecated, lent, staked, or pledged elsewhere)?

| Score | Anchor |
|-------|--------|
| 0 | **Unrestricted** — operator can reuse collateral with no limitation or disclosure. |
| 25 | **Pledged externally** — collateral is used as backing for other obligations (e.g., re-pledged to a prime broker or exchange). Some disclosure, but borrower bears the risk. |
| 55 | **Internal pooling** — collateral is pooled internally for operational efficiency, but not lent or pledged to third parties. Borrower assumes pool risk but not external rehypothecation. |
| 80 | **Contractually prohibited** — reuse is forbidden by contract and/or protocol code, but the prohibition relies on operator honesty (no on-chain enforcement). |
| 100 | **Reuse impossible on-chain** — the collateral UTXO is encumbered so that it cannot be spent to any address other than the borrower's return address within the loan term. Script-enforced non-rehypothecation. |

> **G3 (unrestricted undisclosed rehypothecation) applies when 2b would = 0 and tier ≤ T3.**

---

### 2c — Segregation Verifiability
Can a third party verify that collateral is segregated per-loan?

| Score | Anchor |
|-------|--------|
| 0 | **Unverifiable** — no on-chain evidence that collateral is segregated. Claims of segregation are unsubstantiated. |
| 20 | **Unverifiable (ceiling)** — if no per-loan verification exists, score is capped at 20. |
| 60 | **Pooled addresses** — collateral is held in identifiable addresses, but multiple loans share the same UTXO(s). Per-loan allocation is an off-chain ledger entry. |
| 100 | **Per-loan UTXO** — each loan has its own uniquely identifiable UTXO on-chain. An auditor or borrower can independently verify which output corresponds to which loan. |

---

## Pillar 3 — Verifiability (weight 0.20)

### 3a — Code Transparency
How accessible and reproducible is the code that governs the loan?

| Score | Anchor |
|-------|--------|
| 0 | **Closed** — no source code available. Score cap: ≤15. |
| 15 | **Closed (cap)** — maximum score for closed-source implementations, unless a compelling independent audit fully substitutes. |
| 40 | **Partially open** — some components open, but key modules (e.g., liquidation logic, oracle integration) are closed. |
| 70 | **OSS, non-reproducible** — source is publicly available, but build artifacts cannot be independently verified (no deterministic build). |
| 100 | **Reproducible OSS** — source is public, builds are deterministic, and any third party can verify that deployed bytecode matches source. |

---

### 3b — Audit Coverage
Quantity, recency, and scope of security audits.

| Score | Anchor |
|-------|--------|
| 0 | **No audits** performed, or audits are undisclosed. |
| 25 | **One audit** performed, but it is >18 months old, or used an unqualified firm. |
| 50 | **Multiple audits**, all ≤18 months old, but scope covers smart contracts **only** (no off-chain / operational audit). |
| 75 | **Multiple audits**, ≤18 months, covering smart contracts **and** core off-chain components (oracle, key management, backend). At least two reputable firms. |
| 100 | **Ongoing audit program**, with at least two audits ≤18 months old covering all components (on-chain, off-chain, governance, operations). Results are publicly published. Audits are by top-tier firms with demonstrated Bitcoin/custody expertise. |

> Score >60 requires audit scope to include off-chain components.

---

### 3c — Reserve Attestation
How frequently and transparently does the operator prove collateral backing?

| Score | Anchor |
|-------|--------|
| 0 | **None** — no reserve attestation of any kind. |
| 20 | **One-off attestation** — a single historical proof, no ongoing commitment. |
| 45 | **Assets-only attestation** — regular publication of on-chain addresses / wallet balances but no corresponding liabilities report (proof of reserves without proof of liabilities). |
| 75 | **Scheduled attestation** — periodic (e.g., quarterly or monthly) PoR + PoL published by a qualified third party. |
| 100 | **Live PoR + PoL** — real-time or streamed attestation (e.g., Merkle-tree proof of liabilities updated daily, with on-chain verifiable assets). Any user can independently verify. |

---

### 3d — Price-Feed Integrity
Quality and independence of oracle / price-feed infrastructure.

| Score | Anchor |
|-------|--------|
| 0 | **Closed methodology** — price source is undisclosed or proprietary. |
| 30 | **Open methodology** — feed methodology is documented but only one data source is used, or source is the operator's own trading desk. |
| 55 | **One auditable feed** — single feed, but auditable and from an independent provider (e.g., one trusted oracle). |
| 75 | **Two aggregated feeds** — two independent sources, aggregated (median or mean). |
| 100 | **≥3 independent feeds** — at least three independent, reputable price feeds, aggregated with outlier rejection. Each feed is transparent and auditable. |

---

## Pillar 4 — Operator Resilience (weight 0.18)

### 4a — Track Record
Years in production and market regimes survived.

| Score | Anchor |
|-------|--------|
| 0 | **Launched <6 months ago**, or no real BTC-denominated loan volume. |
| 25 | **6 months to 2 years** in production, has operated through only one market regime. No significant stress event experienced. |
| 50 | **2–4 years** in production, has experienced at least one meaningful market stress (e.g., 2022 BTC drawdown, a liquidation cascade) without loss of customer funds. |
| 75 | **4–6 years** in production, survived multiple market regimes including a severe downturn. Operating history publicly documented. |
| 100 | **>6 years** in production, survived multiple full market cycles including at least one major crisis with demonstrated resilience. Track record of zero principal loss events. |

---

### 4b — Funding Structure
How predictable and sustainable is the operator's cost of funding?

| Score | Anchor |
|-------|--------|
| 0 | **Retroactive repricing** — operator can retroactively change terms or interest rates. |
| 25 | **Uncapped variable** — funding costs can vary without an upper bound (e.g., floating rate with no cap). |
| 50 | **Capped variable** — funding costs are variable but capped or floored (e.g., variable rate + cap). |
| 65 | **Opaque stable** — costs appear stable but the mechanism is not transparent or auditable. |
| 100 | **Term-matched fixed** — all borrowing costs are fixed for the loan term. Fully transparent and auditable. |

---

### 4c — Regulatory Standing
Enforceability of the borrower's claim and relevance of operator licenses.

| Score | Anchor |
|-------|--------|
| 0 | **No license** in a relevant jurisdiction; borrower's claim is unenforceable or untested. Operating without authorization where required. |
| 25 | **Operator has basic registration** (e.g., MSB) but no specific lending or custody license. Legal basis for borrower claim is weak. |
| 50 | **Licensed** in a major jurisdiction (e.g., U.S. state money transmitter, UK FCA, Singapore MAS) with a clear regulatory framework. Borrower has prima facie enforceable rights. |
| 75 | **Multi-jurisdiction licensing**, with a track record of regulatory compliance. Dedicated lending/custody charter or similar. |
| 100 | **Borrower's claim is enforceable by default** without relying on operator license — self-custodial or trust-based structure where regulation is complementary, not essential, to borrower protection. |

---

### 4d — Loss Absorption
Financial buffers protecting borrower collateral in the event of a shortfall.

| Score | Anchor |
|-------|--------|
| 0 | **No loss absorption** — any shortfall falls fully on borrowers. |
| 25 | **Minimum capital** — operator maintains a small capital buffer (<1% of loan collateral) but adequacy is unverified. |
| 50 | **Dedicated guarantee fund** — a verifiable fund (e.g., insurance pool or mutual guarantee fund) covers a meaningful percentage of collateral (≥2%). Terms are documented. |
| 75 | **Multiple layers** — insurance + guarantee fund + operator capital, covering ≥5% of collateral. Policies are with reputable underwriters. Proof of coverage is verifiable. |
| 100 | **Over-collateralization + multi-layer insurance** — loans are over-collateralized at a safe LTV, AND the operator maintains multiple audited loss-absorption layers covering well above historical max drawdowns (≥10% of collateral). |

---

## Pillar 5 — Borrower Exposure (weight 0.12)

### 5a — Identity Surface
What identity information is collected, and what is the breach risk?

| Score | Anchor |
|-------|--------|
| 0 | **KYC + prior data breach** — operator collects full KYC data and has a confirmed history of customer data breach. |
| 40 | **Full KYC** — operator requires full identity verification (name, address, ID) with no known breach, but data is stored centrally. |
| 65 | **Minimal KYC** — operator collects only what is necessary (e.g., email + wallet address). No government ID required. |
| 100 | **No KYC** — borrower can use the service without providing any identity information. Pseudonymous by design (e.g., on-chain proof of BTC ownership / signed message). |

---

### 5b — Disbursement Asset
What asset is the loan disbursed in?

| Score | Anchor |
|-------|--------|
| 0 | **Algorithmic stablecoin** (e.g., UST, FRAX v1-style) — no backing or a fragile algorithmic peg. |
| 25 | **Thin stablecoin** — low-liquidity stablecoin, market cap <$100M, or limited exchange support. |
| 60 | **Top stablecoin** — one of the top 5 by market cap with a verifiable peg and proven track record (e.g., USDC, USDT, DAI). |
| 80 | **Fiat** — loan is disbursed in a major fiat currency (USD, EUR, GBP). Borrower bears fiat FX risk but no stablecoin de-peg risk. |
| 100 | **BTC** — loan is disbursed in native Bitcoin. No disbursement-asset risk. |

---

### 5c — Cost Opacity
How transparent are the total costs of the loan?

| Score | Anchor |
|-------|--------|
| 0 | **Completely opaque** — costs are undisclosed or discovered only at repayment. Hidden fees, origination fees not enumerated, variable costs without disclosure. |
| 25 | **Partial disclosure** — interest rate is disclosed but additional fees (origination, late, prepayment, gas) are not fully enumerated or are unclear. |
| 50 | **Most fees enumerated** — interest, origination, and late fees are listed, but some costs (e.g., network fees, oracle fees) are stated vaguely or subject to change without notice. |
| 75 | **Nearly complete** — all fees are enumerated, with examples and upper bounds. Still some minor opacity in edge-case scenarios. |
| 100 | **All fees fully enumerated** — every possible cost (interest, origination, late, prepayment, network, oracle, service) is listed with clear amounts or formulas. Total cost of borrowing is calculable upfront. Hidden fees = scaled down to 0. |
