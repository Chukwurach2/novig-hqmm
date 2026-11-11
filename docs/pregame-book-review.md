# Reviewing a captured Novig pregame book

Use `review_pregame_book` with the catalog record, parsed book and their actual
local receipt times. Supply previously reviewed event, market and outcome IDs.
The gate checks that the catalog is OPEN before its scheduled start, all mapped
outcomes are TBD, and every displayed level belongs to those outcomes. Reject
closed, settled, unknown or mismatched records and stale, future or misordered
receipts. An outcome may have zero resting levels.

The inputs match the vendored OpenAPI OpenMarketResponse, Outcome and Book
schemas. Book has no provider source timestamp or lifecycle status. This check
bounds local receipt age only. A cached response or a suspension between reads
can still escape the gate. The review neither establishes a paper fill nor
replaces an event-state or order-flow feed. It makes no requests on its own.
