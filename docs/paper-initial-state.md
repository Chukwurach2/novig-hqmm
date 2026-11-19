# Initial paper replay balances

The broker requires finite nonnegative Decimal cash and accumulated stress
fees at construction. Mixed float/string amounts, infinities and NaNs must
fail before quote placement, fee accumulation or settlement. The optional
reservation fee uses the same Decimal units.

Seeded inventory quantities must be nonnegative whole integer contracts.
This buy-only simulator cannot interpret a short or fractional starting
position consistently with its fill and payout accounting. Zero balances
and zero positions are valid. A seeded two-contract winner with no cash
settles to $0.02 under the existing payout unit.

These checks validate the supplied replay state, not its economic history
or cost basis. They do not establish official venue fees, profitability,
short-selling support or live execution. Existing fill, reservation and
settlement behavior remains subject to its separately tested assumptions.
