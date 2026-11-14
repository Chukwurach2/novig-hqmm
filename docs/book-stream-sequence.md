# Consistent Novig snapshots at a fixed sequence

A snapshot sequence identifies a position in one market's book stream. At the
same requested depth, repeated observations may have different local receipt
times. They must describe the same resting orders and priority. Polling now
stops when an equal sequence has different bids. Identical repeats remain
available to existing callers, and a higher sequence can carry a new book.

This check detects contradictory captures within one polling session. It does
not infer intermediate deltas, source timestamps, or fills. The existing
snapshot route and network opt-in are unchanged.

The polling interval must be a finite number of at least one second. Invalid
intervals are rejected before the first snapshot request.
