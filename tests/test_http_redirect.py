from email.message import Message
from io import BytesIO
import unittest
from unittest.mock import patch
from urllib.response import addinfourl

from hqmm.adapters.http import DataError, JsonHTTP


class ReadOnlyHTTPTests(unittest.IsolatedAsyncioTestCase):
    @patch("urllib.request.HTTPSHandler.https_open")
    async def test_redirects_never_trigger_a_second_request(self, https_open):
        headers = Message()
        headers["Location"] = "https://unexpected.invalid/redirect?apiKey=example-token"
        for code in (301, 302, 303, 307, 308):
            with self.subTest(code=code):
                https_open.reset_mock()
                response = addinfourl(BytesIO(), headers, "https://example.invalid/data", code)
                response.msg = "Redirect"
                https_open.return_value = response
                with self.assertRaisesRegex(DataError, f"^Feed HTTP {code};"):
                    await JsonHTTP(allowed=True).get(
                        "https://example.invalid", "/data", {"apiKey": "example-token"}
                    )
                https_open.assert_called_once()
