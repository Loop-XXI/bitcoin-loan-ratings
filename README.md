# Bitcoin-Backed Loan Ratings Network

**Project Anchor** — A public comparison and ratings network for Bitcoin-backed loans.

Built by **Loop LLC** / LedgerRatings.

## Structure

```
/data/providers/{slug}/   — Provider data (profile, evidence, scores, LSI params)
/engine/anchor/           — Anchor Grade engine (qualitative structural rating)
/engine/lsi/              — Liquidation Stress Index (quantitative backtest + bootstrap)
/methodology/             — Canonical methodology (single source of truth)
/site/                    — Next.js application
/supabase/                — Database schema
```

## How scoring works

- Every grade is **deterministically computed** from evidence files
- No hand-edited final scores
- Grade changes happen via evidence-file changes → git-tracked → automatic changelog
- LSI recomputed weekly; grades updated quarterly + event-driven

See `/methodology/` for the full Anchor Framework documentation.
