"""Read-only bounded async transport; no automatic retries or credential logging."""
import asyncio
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


class DataError(RuntimeError):
    pass


class JsonHTTP:
    def __init__(self, allowed=False, timeout=10):
        self.allowed = allowed
        self.timeout = timeout
        self._gate = asyncio.Semaphore(2)

    async def get(self, base, path, params=None):
        if not self.allowed:
            raise DataError("Remote data disabled; confirm provider authorization and location eligibility first")
        if not base.startswith("https://") or not path.startswith("/"):
            raise ValueError("HTTPS base and absolute path required")
        async with self._gate:
            return await asyncio.to_thread(self._get, base + path + "?" + urlencode(params or {}))

    def _get(self, url):
        try:
            with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=self.timeout) as response:
                payload = response.read(10_000_001)
                if len(payload) > 10_000_000:
                    raise DataError("Response too large")
                return json.loads(payload)
        except HTTPError as exc:
            # Never include the URL: reference feed credentials are query parameters.
            raise DataError(f"Feed HTTP {exc.code}; stop and inspect provider quota/status") from None
        except (URLError, TimeoutError, ValueError):
            raise DataError("Feed unavailable or invalid JSON") from None
