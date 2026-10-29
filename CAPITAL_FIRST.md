# v1.6 — Capital-first swing research (read-only)

Policy: NO_TRADE is the default and only signal. The radar prioritizes verified technical data and SEC annual duration facts with matching financial periods. Unmatched/missing/stale financial facts are *not* substituted with earlier arbitrary financial periods. Headlines are unverified claims, never trusted catalysts. The report retains all blockers.

The ranking is **research triage**, not expected profit or a buy list. It sorts by fewer blockers first and attention score second. Even with zero listed blockers, no security can become order-eligible because no causal, prospective evidence or verified primary-source catalyst integration exists yet. Nothing in this package creates, cancels or updates orders. No API trading capability added.

Hypothetical sizing uses the *paper audit* USD capital ceiling divided by three, and the per-position 1% risk allowance divided by twice ATR. It is not an executable quantity or reliable realized-loss limit: stops can slip, gap through or fail to fill, and fractions/fees may restrict actual orders. Do not infer a guarantee of principal protection from the model.

Run `/app/scripts/run.sh test-local` then `/app/scripts/run.sh swing-radar`. Read `/app/reports/swing/latest.json`; inspect `ranking.blockers`, `ranking.hypothetical_risk` and `fundamental.status`. Validate the `radar-daemon` process separately. A normal local scan does not prove automation is active.

The API and price collection remain subject to SEC/Yahoo availability, official market calendars are not integrated, only annual matched revenue/net income are extracted; there is no robust quarterly or valuation comparison. Risk control is informational, NOT an enforced order guard. Neither paper nor real trading is authorized.
