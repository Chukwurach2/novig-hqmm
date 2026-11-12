# Paper queue input checks

Queue ahead is a whole-contract count. Fractional queue inputs can leave
fractional sell flow after queue consumption and therefore fractional paper
fills. Reject such inputs before replacing resting orders. Latency accepts
nonnegative finite seconds, including fractional seconds. One-pass quote
iterables are materialized once so identity validation and placement see
the same quotes.

These offline checks protect replay accounting. Queue depth and latency are
still simulation assumptions and require separate calibration.
