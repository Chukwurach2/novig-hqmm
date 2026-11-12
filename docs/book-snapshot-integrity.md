# Captured Novig book integrity

The paper book schema rejects repeated resting order IDs across the entire
market snapshot. Reusing one order ID within a single outcome or across
outcomes could overstate displayed size and makes the order ambiguous in a
future replay. Separate resting orders at the same price keep their original
order and quantities.

The vendored OpenAPI describes the book sequence as a nonnegative integer and
each book delta as changing one named order. Book snapshots now enforce the
sequence type before any comparison in the polling adapter. A valid snapshot
provides displayed resting size at its captured depth. Paper fills still
require separate observed sell flow.
