# Development roadmap

1. **Contract identity and authorized capture**: build reviewed event/outcome mapping
   with period, line, start, void and payout semantics; append timestamped raw data
   locally under the provider license; enforce quotas/backoff and suspend states.
   Done when mismatched contracts and stale/future source timestamps are rejected.
2. **Replay and fees**: verify fee calculation, charge timing, rebates and rounding
   with current official examples; add recorded trade/order replay, partial fills,
   order reservation, source delay and queue calibration; implement PUSH refunds.
   Done when recorded examples reconcile in cents and fills cannot see future data.
3. **Fair-value study**: multi-book weighting, uncertainty, leave-one-book-out
   sensitivity and calibration; chronological train/validation/test splits.
   Done when models beat predeclared baselines out of sample after cost stress.
4. **Risk and attribution**: event/league/portfolio exposure, correlated positions,
   loss limits, drawdown stops, markout attribution and inventory liquidation costs.
   Done when scenario tests cap worst-case loss across correlated outcomes.
5. **Streaming and forward paper trial**: websocket gap recovery, lifecycle handling,
   durable research logs and monitoring; complete manual eligibility/API-permission
   checks. Run forward paper trading long enough to estimate uncertainty by event.

Any future live execution is a separate explicitly authorized project with its own
geographic/account/automation review. There is no live-mode switch in this starter.
