# News First — Internal simulation (research only)

Git First reviewed upstream `Jakeschincariol/day-trader-skill` main:
- `trader-news/news.py`: Yahoo headlines + SEC 8-K; reuse as reference, no broker write.
- `trader-analyst/facts.py`: SEC company facts; not historical analyst consensus.
- `trader-entry/entry.py`: completed-bar timing for LONG; no news-driven verified entry.

New glue only: `src/news_first_sim.py`. Processes existing `event-verify` JSON, issues EVIDENCE_PENDING research signals and idempotently appends NO_TRADE decisions to a local JSONL journal. No fake entries or prices. No broker endpoint or execution code. `orders_sent=0` and `authorized_to_trade=false`.

To run after `news-audit`, `news-catalog`, `event-verify`:

```
/app/scripts/run.sh news-sim
```

Outputs:
- `/app/reports/news/simulation-signals.json`
- `/app/reports/news/simulation-journal.jsonl`

No positions opened until an independent evidence+causal price validation module exists; this is a decision journal, not a complete P&L simulator.
