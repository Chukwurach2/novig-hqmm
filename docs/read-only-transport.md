# Read-only feed redirects

The feed transport stops at an HTTP redirect and reports the status code.
Review the configured provider destination before another request. This keeps
an authorized GET to a configured endpoint from automatically becoming a
request to a different origin or path. This matters when query strings contain
provider credentials. The error omits both request and redirect URLs.

Offline tests simulate redirects and count transport calls. The existing
opt-in network guard, request timeout, response size bound, and no-retry
behavior still apply.
