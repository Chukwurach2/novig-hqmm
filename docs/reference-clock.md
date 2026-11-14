# Elapsed time for reference freshness

Reference freshness compares UTC instants. When two local datetimes share a
time zone, subtracting them directly can ignore a daylight-saving transition.
During the repeated fall hour, stale and future quotes can then appear to
have the same timestamp as the decision. During the spring jump, a recent
quote can appear an hour older. UTC normalization preserves the existing
inclusive maximum age and future-quote rejection. The regression covers both
transitions offline.

The configured maximum age must be finite and positive. Infinite, NaN,
boolean and nonpositive values fail before a quote enters the estimate.
This preserves the caller's finite freshness limit for the baseline and
leave-one-book-out calculations.
