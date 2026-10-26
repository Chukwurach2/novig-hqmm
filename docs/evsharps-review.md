# EVSharps exploration and product destination

Inspected through the signed-in browser on 2026-10-19. This records interface capabilities and stated methodology, not independently verified betting results. No subscriber tables, account settings or personal betting data are reproduced.

## Coverage of this review

Opened the NFL/MLB/NBA/NHL/More navigation sections; inspected touchdown help, betting-book selection, de-vig reference/method menus, reference eligibility, boosts, odds range, liquidity filters, historical window/price/staking menus and customization. Visited Recommendations, Arbs & Middles, NFL Line Movement, NFL Devig Results, Calculators (both tabs) and NFL Live.

This is a broad feature inventory and a detailed review of representative workflows, not an exhaustive test of every sport, every filter combination or every settlement calculation. No watchlist, saved preset, bankroll or account changes were made.

## Site map

| Section | Pages visible in navigation |
|---|---|
| NFL (16 pages) | Anytime TD; player props; first/last TD; 2+ TD; ATTD parlays; main lines; de-vig results; preseason; futures; college props/main; live; NFL/college trackers; main recap; movement |
| MLB (22) | Home runs; homer parlays; strikeouts; props; main; 2+ HR; futures; bets/recaps; live/feed; batter-v-pitcher; matchups/stats/barrels; pitcher and strikeout previews; pitcher mix/top pitches; trends; movement |
| NBA (12) | All props; main; threes; points/rebounds/assists; college basketball; WNBA props/main; recap/results; movement; KOTC; live |
| NHL (14) | Anytime/2+/first goals; props/main; goal parlays; de-vig results; live/tracker; recap/results; goal grades; longshots; movement |
| More (14) | Recommendations; arbs/middles; calculators; all-sport movement; heat map; cheat sheets; outliers by sport; bonus-bet hedges; college baseball; soccer; World Cup; UFC |

Free/Analyst/Sharp labels appear on navigation entries. Presence in navigation does not establish complete data or entitlement for every destination. Account/security/payment controls were outside this review.

## Market-table controls

- **Betting books**: choose the venues eligible to supply the displayed best offer. All/None and individual selection are available.
- **Exclude**: help states exclusions can apply per page or across pages. Separate from fair-value reference exclusions.
- **De-vig reference**: market average, individual books, weighted custom mixes and equal-weight blends; search, favorites and prop tags. Existing personal mix values are intentionally omitted.
- **Method**: Worst-Case, Additive, Multiplicative, Power, Probit. Menu labels were verified; their exact implementations were not audited.
- **Reference eligibility**: each book can be used if priced, required, or excluded. All requires included references; Any allows whichever are available. Changing availability can change the effective reference basket.
- **Prop/Game**: market and event selection controls are present; player/prop searches are also present in table headers.
- **Boost**: None, percentage presets, No Sweat and Custom. Eligibility, caps and exact payout treatment require inspection before use.
- **Range**: minimum/maximum American odds.
- **Advanced filters**: AND/OR matching, over/under/EV-side exchange-liquidity rules, venue selection, dollar thresholds, odds range and minimum estimated team points. Saved-filter management exists.
- **Record window**: All-time, SZN, L3/L7/L14/L30/L60.
- **Historical Prices**: Close or Open on preset records.
- **Historical Staking**: Flat 1u or quarter Kelly.
- **Display**: stacked view, show/hide odds, unit/dollar display, Kelly sizing header, customizable/reorderable columns and saved defaults. Other view modes were not enumerated.
- **Watchlist/betslip**: watchlist toggles are visible. Help says plus controls add plays to the site's betslip; these were deliberately not used.

## Data available in the touchdown view

Best offer/book, estimated EV, estimated fair odds and probability, sizing, source-age indicators, book weights, over/under odds, exchange quoted amounts, earliest captured price, game logs, current/prior-year hit rates, estimated team points, opponent positional defense, defense sample size, snaps/snap share, targets/team and position shares, red-zone usage and team rank.

These are different kinds of evidence. Usage and hit rates are descriptive context; consensus fair values are estimates; quoted capacity is not a reserved fill. Do not equate them with a proven independent prediction.

The Customize explanation defines Open as the earliest captured same-book selection/line price after at least four sportsbooks quote it, without boosts. It explicitly distinguishes this from a verified sportsbook opening price.

## Representative research workflows

### Recommendations
https://www.evsharps.com/recommendations

The inspected page presents current offers and a Performance tab, sport/market/book filters, reference-group detail, estimated EV and conservative floor, fair odds/minimum acceptable odds, liquidity status and qualification details.

Its stated screen requires estimated EV after fees of at least 3%, a conservative estimate of at least 1%, at least three other reference groups, exclusion of the offered venue from its own estimate, quotes within ten minutes, pregame with at least five minutes to start, odds between -250 and +600, and bounded reference disagreement. It applies selection limits by book/sport/game/player.

The site explicitly describes the conservative estimate as a sensitivity check, not a statistical confidence interval. These are provider statements, not independently verified guarantees. Detailed Performance-tab calculations were not audited.

### Arbs & Middles
https://www.evsharps.com/arb

Controls include total budget, opportunity type, sport/prop, betting venues, exchange-capacity requirement, number of results, minimum worst-case return and a manual two-price calculator. Results display leg prices, stakes, fee assumptions, quoted capacity, update times and profit-by-outcome details.

The page distinguishes an arb with positive profit in all modeled outcomes from a middle whose both-win payout is conditional. It warns ordinary sportsbook limits may be unknown, liquidity is not reserved, source timestamps do not establish individual quote freshness, and exact side/line/settlement must match. These caveats must become explicit paper-simulation rejection rules.

### Line Movement
https://www.evsharps.com/movement?sport=nfl

Sport, player/team, prop, side, fair-value reference, mover direction and chart scale controls; exact-line charts; first/latest fair probabilities, source books, capture times and point counts. The inspected page states today-only history resetting at midnight Eastern, with pregame captures about every thirty minutes.

Suitable for coarse price-leadership research and decision audits. It is not sufficient by itself for subsecond latency or market-making fill studies. Historical persistence/export access must be confirmed.

### Devig Results
https://www.evsharps.com/devig-results?sport=nfl

Date/window, betting venue, market, archived/opening odds, flat/quarter-Kelly staking, reference and method filters; daily profit, coverage, settled/pending/ungraded counts, strategy rankings, minimum-sample and profitable-only filters; an Export CSV control is present. No export was downloaded or redistributed.

The page explicitly says offers at different books are alternatives, not a unique-bet portfolio. Incomplete grading and uneven archive coverage are visible. Selecting the best result among many methods on the same sample is exploratory selection; it requires a new untouched evaluation period. Export permission, schema, fee handling and selection timestamps still need verification.

### Calculators
https://www.evsharps.com/calculators

Arbitrage balancing and an odds converter (fractional/decimal/American/implied probability, stake, profit and payout). The converter explicitly excludes fees. Calculator output must not be mistaken for a fully executable multi-venue trade.

### Live
https://www.evsharps.com/live?sport=nfl

Book/reference/side/game/boost/range/display controls and the comparison-table schema were visible. No populated live rows appeared during inspection. Live coverage and source latency remain unverified.

## Product destination

Build a decision-support system that answers:
1. Which exact available offer is plausibly mispriced?
2. What independent evidence supports the fair probability?
3. At what price does the edge disappear after costs?
4. How much size is actually available and what exposure would result?
5. Did this method work on future, previously unseen opportunities?

Two complementary strategy tracks:
- **Taking value**: compare currently available bets against validated independent fair values; surface exact venue/contract/price thresholds, freshness, fees, uncertainty and capacity.
- **Providing liquidity on Novig**: estimate when a resting bid earns enough spread to compensate for being filled by better-informed traders, time delay and inventory risk; test in paper replay and forward paper trading.

EVSharps can help source research questions and benchmark outputs. The project's contribution must be verified contract identity, honest timing, independent evaluation, realistic costs/fills, risk controls and a durable decision ledger. Simply reproducing the site's green EV numbers would add little.

## Delivery sequence and exit criteria

1. **Research-ready inputs**: permitted export/API or manual observations, explicit mappings, source timestamps, lifecycle and fee rules. Reject ambiguous identity, unavailable quotes and unsupported settlement.
2. **Usable paper opportunity report**: exact venue/event/market/outcome/line, observed time/expiry, offered price/size, estimated fair probability, uncertainty, break-even price, net EV and reason to accept/reject.
3. **Forward evidence**: freeze a hypothesis and record every qualifying opportunity before outcomes, including no-fills and rejected offers; evaluate event-clustered uncertainty, price movement after decisions, net results, drawdown, costs and feasible capacity.
4. **Decision**: retain, revise or reject each strategy based on evidence. If no credible edge survives, explicitly report that result.

The immediate milestone is a real-data paper opportunity ledger with reproducible evidence—not more infrastructure indefinitely. A stable alert/dashboard is a subsequent delivery once data rights and validation support it. A live execution bot is outside the current authorization.

## Next work

- Verify supported EVSharps CSV export/API rights and obtain schemas without publishing licensed raw data.
- Use Recommendations as a comparison benchmark, not ground truth; test independent estimates with the offered venue excluded.
- Implement distinct opportunity schemas for one-sided value, paired arbitrage, middles and maker quotes.
- Add break-even price thresholds, stale/missing/insufficient-capacity rejections and identity checks.
- Avoid counting alternative venues as independent bets; group exposure and evaluation by event.
- Inspect remaining sport-specific research pages and performance/export methodology as targeted follow-ups.
