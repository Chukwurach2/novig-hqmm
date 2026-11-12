# Sportsbook reference source time

For each parsed head-to-head reference, prefer its market update timestamp. If
the market omits that field, the adapter keeps its existing bookmaker-level
fallback. The fallback indicates the bookmaker snapshot time and provides
coarser evidence about the age of an individual market.

A present but invalid market timestamp fails parsing, even when the bookmaker
timestamp is usable. The same applies when both timestamps are missing. The
reference schema requires a timezone and the fair-value baseline excludes stale
and future references at evaluation time. The adapter uses provider time
throughout.
