from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest
from unittest.mock import AsyncMock, patch

from hqmm.adapters.novig import NovigData
from hqmm.schemas import Book, Level


class BookStreamSequenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_equal_sequence_requires_same_depth_and_priority(self):
        at = datetime(2026, 11, 13, tzinfo=timezone.utc)
        bids = (Level("home", "a", Decimal(".5"), 20),
                Level("home", "b", Decimal(".5"), 10),
                Level("away", "c", Decimal(".4"), 5))
        first = Book("market", 8, at, bids)
        repeated = replace(first, received_at=at + timedelta(seconds=1),
                           bids=(bids[2], *bids[:2]))
        advanced = replace(first, sequence=9, bids=(bids[1],))
        conflicting = replace(advanced, bids=bids)
        data = NovigData(None)
        data.book = AsyncMock(side_effect=[first, repeated, advanced, conflicting])
        with patch("hqmm.adapters.novig.asyncio.sleep", new_callable=AsyncMock):
            stream = data.stream("market")
            self.assertIs(await stream.__anext__(), first)
            self.assertIs(await stream.__anext__(), repeated)
            self.assertIs(await stream.__anext__(), advanced)
            with self.assertRaisesRegex(ValueError, "conflicting"):
                await stream.__anext__()
            with self.assertRaises(StopAsyncIteration):
                await stream.__anext__()
