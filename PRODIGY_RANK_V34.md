# Rising Stars / Prodígios — v3.4

Read-only secondary ranking. Keeps consolidated 180d ranking separate.

`/app/scripts/run.sh prodigy-rank`

Input: existing Collective2 `*_closed_trades.json` in `/app/reports/providers/raw`.
Output: `/app/reports/intelligence/prodigy-top10-latest.json`.

- Rolling 60-day window; 5+ closed trades and 2+ active weeks for candidacy.
- Beta-binomial style shrinkage: (wins+10)/(trades+20), a neutral 50% prior.
- Heuristic score includes shrinked win rate and active weeks; score is not an expected return, is not calibrated, and does not establish an edge.
- No-loss streaks flagged for uncertainty, not excluded automatically.
- Trades with missing/wrong API status fail closed.
- No broker orders, no subscription, no Paper authorization; no exposure allocation from this research score.
- Profits from Collective2 may be gross of some costs and cannot be assumed reproducible; this screen is about candidate discovery, not reliable win-rate prediction.

Proposed Paper risk for a prodigy (R$ 20) requires separate downstream gateway implementation and explicit approval before automated copies; NOT implemented here.
