# Reference-book sensitivity

The proportional de-vig baseline gives every fresh reference operator equal
weight after normalizing its implied probabilities. For a reviewed offer,
`leave_one_book_out` excludes the offered operator and requires at least two
fresh reference operators. It returns the full consensus, each consensus with
one reference removed, and the resulting range for each outcome. The same
freshness, exact contract and duplicate-operator checks apply to every result.

Use reviewed exact contract mappings and canonical operator IDs before calling
the function. Affiliated books or books using shared pricing may still move
together. The range describes sensitivity to the reference set. It provides
neither a statistical interval nor evidence of independent pricing. Existing
reports and published picks do not consume this diagnostic automatically.
