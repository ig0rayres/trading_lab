# v2.5: Event evidence triage (read-only)

## Commands

```sh
/app/scripts/run.sh event-verify
```

Input: `/app/reports/news/catalog.json` from complete `news-audit` -> `news-catalog`.
Output: `/app/reports/news/evidence-triage.json`.

This is NOT automatic independent event verification. It creates a manual review queue, flags issuer name matches and potential duplicates without merging them, and explicitly retains all records as UNVERIFIED and NO_TRADE. The issuer heuristic currently knows AAPL/MSFT/NVDA and should be extended only with a controlled alias registry.

Next separate research task: locate official primary documents per event, verify contemporaneous consensus and original release time, then design a causally valid event-driven replay. DO NOT use the triage output as trade signals.
