#!/usr/bin/env python3
"""Estimate a TWD portfolio value from a local JSON file and public quotes."""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_portfolio(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("holdings"), list) or not data["holdings"]:
        raise ValueError("holdings must be a nonempty list")
    for item in data["holdings"]:
        if not isinstance(item, dict) or item.get("market") not in ("TW", "US"):
            raise ValueError("each holding needs market TW or US")
        if not isinstance(item.get("symbol"), str) or not item["symbol"].strip():
            raise ValueError("each holding needs a symbol")
        if not isinstance(item.get("shares"), (int, float)) or isinstance(item["shares"], bool) or item["shares"] <= 0:
            raise ValueError("each holding needs positive shares")
        if not isinstance(item.get("pledged", False), bool):
            raise ValueError("pledged must be a boolean")
        if item["market"] == "US" and item.get("pledged", False):
            raise ValueError("pledged US holdings are not supported")
    for key in ("cash_twd", "loan_twd"):
        value = data.get(key)
        if value is None:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} must be a nonnegative number")
    return data


def yahoo_quote(symbol):
    encoded = urllib.parse.quote(symbol, safe="")
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{encoded}?interval=1d&range=5d"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.load(response)["chart"]["result"][0]
        meta = result["meta"]
        price = meta.get("regularMarketPrice")
        stamp = meta.get("regularMarketTime")
        if price is None or price <= 0 or stamp is None:
            return None
        return {"price": price, "as_of_utc": datetime.fromtimestamp(stamp, timezone.utc).isoformat(),
                "source": "Yahoo Finance", "price_type": "latest available quote; may be delayed or previous close"}
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError, TypeError):
        return None


def quote_holding(item, fetch=yahoo_quote):
    symbol = item["symbol"].strip().upper()
    candidates = [symbol] if item["market"] == "US" else [f"{symbol}.TW", f"{symbol}.TWO"]
    for candidate in candidates:
        quote = fetch(candidate)
        if quote:
            return candidate, quote
    return None, None


def value_portfolio(data, fetch=yahoo_quote):
    holdings = []
    missing = []
    tw_value = pledged_value = us_value = 0.0
    missing_pledged = False
    for item in data["holdings"]:
        resolved, quote = quote_holding(item, fetch)
        market = item["market"]
        amount = quote["price"] * item["shares"] if quote else None
        if amount is None:
            missing.append(item["symbol"])
            if item.get("pledged", False):
                missing_pledged = True
        elif market == "US":
            us_value += amount
        elif item.get("pledged", False):
            pledged_value += amount
        else:
            tw_value += amount
        holdings.append({"symbol": item["symbol"], "market": market, "shares": item["shares"],
                         "pledged": item.get("pledged", False), "quote_symbol": resolved,
                         "quote": quote, "value_native": amount, "currency": "USD" if market == "US" else "TWD"})
    has_us = any(item["market"] == "US" for item in data["holdings"])
    fx = fetch("USDTWD=X") if has_us else None
    if has_us and not fx:
        missing.append("USDTWD=X")
    complete = not missing
    market_twd = tw_value + pledged_value + us_value * (fx["price"] if fx else 0) if complete else None
    loan = data.get("loan_twd")
    cash = data.get("cash_twd")
    pledged_total = None if missing_pledged else pledged_value
    coverage = pledged_total / loan * 100 if pledged_total is not None and loan is not None and loan > 0 else None
    return {"calculated_at_utc": datetime.now(timezone.utc).isoformat(), "valuation_complete": complete,
            "missing_quotes": missing, "holdings": holdings, "usd_twd": fx,
            "summary": {"tw_value_twd": tw_value if complete else None,
                        "pledged_value_twd": pledged_total,
                        "us_value_usd": us_value if complete else None,
                        "market_value_twd": market_twd, "cash_twd": cash, "loan_twd": loan,
                        "assets_twd": market_twd + cash if complete and cash is not None else None,
                        "net_assets_twd": market_twd + cash - loan if complete and cash is not None and loan is not None else None,
                        "pledge_coverage_percent": coverage}}


def main():
    parser = argparse.ArgumentParser(description="Estimate portfolio value in TWD")
    parser.add_argument("--portfolio", required=True, help="Path to a private JSON portfolio file")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()
    try:
        result = value_portfolio(load_portfolio(args.portfolio))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Portfolio input error: {exc}\n")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in result["holdings"]:
            quote = item["quote"]
            detail = f'{quote["price"]} {item["currency"]} at {quote["as_of_utc"]}' if quote else "quote unavailable"
            print(f'{item["symbol"]}: {detail}; shares={item["shares"]}; value={item["value_native"]}')
        if result["usd_twd"]:
            print(f'USD/TWD: {result["usd_twd"]["price"]} at {result["usd_twd"]["as_of_utc"]}')
        if not result["valuation_complete"]:
            print("Incomplete valuation; missing: " + ", ".join(result["missing_quotes"]))
        print("Summary: " + json.dumps(result["summary"], ensure_ascii=False))
    return 0 if result["valuation_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
