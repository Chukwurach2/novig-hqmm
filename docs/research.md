# Research protocol

Start with pregame, two-outcome moneyline markets and unambiguous settlement rules.
Store decision-time source timestamps and receipt times; join only data available
at that decision. Group related outcomes by event when splitting and bootstrapping.
Reject unavailable/suspended/started markets and quotes based on stale sources.

Pre-register threshold/spread/skew settings and a date-based holdout before tuning.
Compare no-trade, Novig midpoint, single-book, equal-weight de-vig and static quotes.
Treat sportsbook consensus as a noisy baseline, not ground truth or independent
votes. Price leadership and correlated feeds can create false apparent edge.

Report gross/net P&L, fee dollars, calibration/Brier score, event-clustered confidence
intervals, fill rate, inventory, turnover, drawdown and 1/5/30-second markouts.
Sweep source delay, queue ahead, fee assumptions and fill probabilities. Include
all rejected/no-fill opportunities. Separate settlement P&L from marked equity.

Advance only with positive held-out net results robust to plausible costs and
adverse-selection stress. The included demo only validates plumbing and arithmetic;
it provides no market data, forecasting evidence or deployable profitable strategy.
