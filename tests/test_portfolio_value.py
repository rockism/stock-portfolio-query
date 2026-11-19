import json
import tempfile
import unittest
from pathlib import Path

from portfolio_value import load_portfolio, value_portfolio


DATA = {"holdings": [
    {"market": "TW", "symbol": "2330", "shares": 10},
    {"market": "TW", "symbol": "0050", "shares": 20, "pledged": True},
    {"market": "US", "symbol": "AAPL", "shares": 2}],
    "cash_twd": 1000, "loan_twd": 500}


def quote(price):
    return {"price": price, "as_of_utc": "2026-01-01T00:00:00+00:00", "source": "test", "price_type": "test"}


class PortfolioTests(unittest.TestCase):
    def test_complete_value(self):
        prices = {"2330.TW": 100, "0050.TW": 50, "AAPL": 200, "USDTWD=X": 30}
        result = value_portfolio(DATA, lambda symbol: quote(prices[symbol]) if symbol in prices else None)
        self.assertTrue(result["valuation_complete"])
        self.assertEqual(result["summary"]["market_value_twd"], 14000)
        self.assertEqual(result["summary"]["net_assets_twd"], 14500)
        self.assertEqual(result["summary"]["pledge_coverage_percent"], 200)

    def test_missing_quote_suppresses_aggregate(self):
        result = value_portfolio(DATA, lambda symbol: None)
        self.assertFalse(result["valuation_complete"])
        self.assertIsNone(result["summary"]["net_assets_twd"])
        self.assertIn("USDTWD=X", result["missing_quotes"])

    def test_ratio_available_when_unrelated_quote_missing(self):
        prices = {"0050.TW": 50}
        result = value_portfolio(DATA, lambda symbol: quote(prices[symbol]) if symbol in prices else None)
        self.assertFalse(result["valuation_complete"])
        self.assertEqual(result["summary"]["pledge_coverage_percent"], 200)

    def test_unknown_loan_omits_ratio_and_net_assets(self):
        data = dict(DATA)
        data.pop("loan_twd")
        prices = {"2330.TW": 100, "0050.TW": 50, "AAPL": 200, "USDTWD=X": 30}
        result = value_portfolio(data, lambda symbol: quote(prices[symbol]) if symbol in prices else None)
        self.assertIsNone(result["summary"]["pledge_coverage_percent"])
        self.assertIsNone(result["summary"]["net_assets_twd"])

    def test_unknown_cash_omits_asset_totals(self):
        data = dict(DATA)
        data.pop("cash_twd")
        prices = {"2330.TW": 100, "0050.TW": 50, "AAPL": 200, "USDTWD=X": 30}
        result = value_portfolio(data, lambda symbol: quote(prices[symbol]) if symbol in prices else None)
        self.assertEqual(result["summary"]["market_value_twd"], 14000)
        self.assertIsNone(result["summary"]["assets_twd"])
        self.assertIsNone(result["summary"]["net_assets_twd"])

    def test_missing_input_fails(self):
        with self.assertRaises(FileNotFoundError):
            load_portfolio("/no/such/portfolio.json")

    def test_invalid_holding_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "portfolio.json"
            path.write_text(json.dumps({"holdings": []}))
            with self.assertRaises(ValueError):
                load_portfolio(path)


if __name__ == "__main__":
    unittest.main()
