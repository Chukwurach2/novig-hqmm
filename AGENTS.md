# Contributor instructions
This is a paper-only research platform. Never add live execution, order signing,
trading credentials, location spoofing, or geofence bypasses as routine changes.
Keep all external interfaces GET-only. Default commands must work offline.
Check docs/spec/novig-openapi-v3.json before changing Novig fields or routes.
Use explicit event/outcome mapping; never match by display name alone.
All financial units use Decimal. Novig contract payout is $0.01.
Validate with `PYTHONPATH=src python -m unittest discover -s tests -v` and
`PYTHONPATH=src python -m hqmm.cli`. Add tests for changed financial behavior.
Do not commit .env, credentials, licensed raw feeds, or private research data.
