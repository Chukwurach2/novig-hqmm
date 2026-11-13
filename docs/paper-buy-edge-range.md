# Paper buy sensitivity to fair value and costs

For one reviewed Novig outcome, pass the lower and upper fair probabilities,
exact bid price and hypothetical whole-contract fill size to
`buy_edge_range`. It applies the existing fee and adverse-selection stress
cost to each bound, then scales by the one-cent contract payout and fill
size. The result is a pair of Decimal dollar estimates. A range crossing
zero means the edge depends on where fair probability falls in the input
range. For example, 100 contracts at 0.50 with fair probability 0.49–0.53
and default costs produce a range of −$0.016 to +$0.024.

The inputs describe a single contract and assumed fill. A reference-book
omission range measures dependence on the reference set. It does not supply
a confidence interval. The cost parameters remain paper assumptions while
API fee units and rounding are under review. The helper does not select
trades, assume fills, or round the range to currency display precision.
