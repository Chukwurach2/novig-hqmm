import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D
from pathlib import Path
from hqmm.schemas import Reference, Quote, Level
from hqmm.fair_value import estimate
from hqmm.edge import Costs, buy_edge
from hqmm.quoting import quote_binary, GRID
from hqmm.paper import PaperBroker
from hqmm.adapters.novig import NovigData, BASE, MARKETS, BOOK
from hqmm.adapters.reference import SportsbookData
from hqmm.adapters.http import JsonHTTP, DataError

ROOT=Path(__file__).resolve().parents[1]
NOW=datetime(2026,1,1,tzinfo=timezone.utc)
MID='00000000-0000-0000-0000-000000000001'

def ref(at=NOW,book='b'):
    return Reference('e',book,'h2h',('A','B'),(D('1.8'),D('2.2')),at)

def q():return Quote('m','A',D('.5'),100,NOW,NOW+timedelta(seconds=10))

class Finance(unittest.TestCase):
    def test_devig_reordered(self):
        other=Reference('e','b2','h2h',('B','A'),(D('2.2'),D('1.8')),NOW)
        fair=estimate([ref(),other],NOW)
        self.assertAlmostEqual(fair['A'],D('.55'))
        self.assertAlmostEqual(sum(fair.values()),D(1))

    def test_bad_references(self):
        for rows in ([ref(at=NOW-timedelta(seconds=31))],[ref(at=NOW+timedelta(seconds=1))],[ref(),ref()],
                     [ref(),Reference('other','b2','h2h',('A','B'),(D(2),D(2)),NOW)]):
            with self.assertRaises(ValueError):estimate(rows,NOW)

    def test_validation(self):
        for x in ('NaN','Infinity','-.1','1'):
            with self.assertRaises(ValueError):Level('A','id',D(x),1)
        with self.assertRaises(ValueError):ref(at=datetime(2026,1,1))
        with self.assertRaises(ValueError):Costs(D(-1))

    def test_edge(self):
        self.assertEqual(buy_edge(D('.6'),D('.55'),Costs(D('.01'),D('.02'))),D('.02'))

    def test_skew_limits_grid_and_no_edge(self):
        fair={'A':D('.6'),'B':D('.4')}
        empty=quote_binary('m',fair,{},NOW,Costs())
        loaded=quote_binary('m',fair,{'A':950},NOW,Costs())
        a=next(x for x in loaded if x.outcome_id=='A')
        self.assertLess(a.price,empty[0].price)
        self.assertEqual(a.contracts,50)
        self.assertTrue(all(x.price in GRID for x in loaded))
        self.assertEqual(quote_binary('m',fair,{},NOW,Costs(D('.9'))),[])
        self.assertFalse(any(x.outcome_id=='A' for x in quote_binary('m',fair,{'A':1000},NOW,Costs())))
        with self.assertRaises(ValueError):quote_binary('m',{'A':D('.5'),'B':D('.3'),'C':D('.2')},{},NOW,Costs())

    def test_queue_latency_units_fee_and_settlement(self):
        p=PaperBroker(D(10));p.replace([q()],queue_ahead=100,latency_seconds=1)
        self.assertEqual(p.inventory,{})
        self.assertEqual(p.sell_flow('m','A',D('.5'),200,NOW),[])
        fills=p.sell_flow('m','A',D('.5'),150,NOW+timedelta(seconds=2),D('.01'))
        self.assertEqual(fills[0]['contracts'],50)
        self.assertEqual(p.cash,D('9.745'))
        self.assertEqual(p.fees_usd,D('.005'))
        self.assertEqual(p.equity({('m','A'):D('.6')}),D('10.045'))
        self.assertEqual(p.sell_flow('m','A',D('.6'),100,NOW+timedelta(seconds=3)),[])
        self.assertEqual(p.sell_flow('m','A',D('.5'),100,NOW+timedelta(seconds=10)),[])
        with self.assertRaises(ValueError):p.settle('m',{})
        p.settle('m',{'A':D(1)})
        self.assertEqual(p.cash,D('10.245'))
        with self.assertRaises(ValueError):p.settle('m',{'A':D(1)})
        with self.assertRaises(ValueError):p.replace([q()])

    def test_cash_and_position_caps(self):
        for cash,cap,n in ((D('.01'),1000,2),(D(100),3,3)):
            p=PaperBroker(cash,cap);p.replace([q()],queue_ahead=0,latency_seconds=0)
            self.assertEqual(p.sell_flow('m','A',D('.5'),100,NOW,D(0))[0]['contracts'],n)
            self.assertGreaterEqual(p.cash,0)
            self.assertEqual(p.sell_flow('m','A',D('.5'),100,NOW,D(0)),[])

class FakeHTTP:
    def __init__(self,pages):self.pages,self.calls=list(pages),[]
    async def get(self,*args):
        self.calls.append(json.loads(json.dumps(args)))
        return self.pages.pop(0)

class Adapters(unittest.IsolatedAsyncioTestCase):
    async def test_remote_disabled(self):
        with self.assertRaises(DataError):await JsonHTTP().get(BASE,MARKETS)

    async def test_pagination(self):
        h=FakeHTTP([{'items':[{'marketId':'a'}],'next':'opaque'},{'items':[{'marketId':'b'}]}])
        self.assertEqual([x['marketId'] async for x in NovigData(h).markets()],['a','b'])
        self.assertEqual(h.calls[1][2]['after'],'opaque')

    async def test_repeated_cursor(self):
        h=FakeHTTP([{'items':[],'next':'x'},{'items':[],'next':'x'}])
        with self.assertRaises(ValueError):[x async for x in NovigData(h).markets()]

    async def test_book_contract(self):
        h=FakeHTTP([{'marketId':MID,'seq':5,'orders':{'A':[{'orderId':'o','price':'.55','qty':100}]}}])
        book=await NovigData(h).book(MID)
        self.assertEqual(book.bids[0].contracts,100)
        self.assertEqual(book.bids[0].price,D('.55'))
        self.assertEqual(h.calls[0][1],BOOK.format(id=MID))
        with self.assertRaises(ValueError):await NovigData(h).book(MID,21)

    async def test_reference_contract(self):
        payload=[{'id':'e','bookmakers':[{'key':'b','last_update':'2026-01-01T00:00:00Z',
            'markets':[{'key':'h2h','outcomes':[{'name':'A','price':1.8},{'name':'B','price':2.2}]}]}]}]
        h=FakeHTTP([payload]);rows=await SportsbookData(h,'fake').snapshot()
        self.assertEqual(rows[0].decimal_odds,(D('1.8'),D('2.2')))
        self.assertEqual(h.calls[0][2]['oddsFormat'],'decimal')

class Contracts(unittest.TestCase):
    def test_vendored_spec(self):
        raw=(ROOT/'docs/spec/novig-openapi-v3.json').read_bytes();spec=json.loads(raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),json.loads((ROOT/'docs/spec/provenance.json').read_text())['sha256'])
        self.assertIn(BASE,[x['url'] for x in spec['servers']])
        for path in (MARKETS,BOOK):self.assertIn('get',spec['paths'][path])
        self.assertEqual(spec['paths'][BOOK]['get']['responses']['200']['content']['application/json']['schema']['$ref'],'#/components/schemas/Book')
        self.assertEqual(set(spec['components']['schemas']['Book']['required']),{'marketId','seq','orders'})
        self.assertIn('1¢',spec['components']['schemas']['RestingOrder']['properties']['qty']['description'])

    def test_offline_demo_and_live_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            run=subprocess.run([sys.executable,'-m','hqmm.cli','--output',d+'/demo.json'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertTrue(json.loads(Path(d+'/demo.json').read_text())['synthetic'])
            run=subprocess.run([sys.executable,'-m','hqmm.cli'],cwd=ROOT,env=dict(os.environ,HQMM_MODE='live'),capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            self.assertIn('Only paper',run.stderr)
