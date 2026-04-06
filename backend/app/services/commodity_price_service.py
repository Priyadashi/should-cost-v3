"""
Commodity price fetcher using Yahoo Finance (unofficial API).
Sources:
  - MCX India tickers (e.g. COPPER.MCX) — prices already in INR/kg
  - COMEX/LME tickers (e.g. HG=F) — prices in USD, converted to INR via USDINR=X
Results are cached in-memory for 15 minutes to avoid hammering Yahoo Finance.
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional

_cache: dict[str, dict] = {}
_CACHE_TTL = timedelta(minutes=15)

_YF_BASE = "https://query2.finance.yahoo.com/v8/finance/chart"
_YF_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://finance.yahoo.com",
}

# Ticker definitions
# factor: float → multiply raw Yahoo price by this to get INR/kg
# factor: "USD_LB"  → raw price is USD/lb, needs USDINR rate
# factor: "USD_TROY" → raw price is USD/troy oz, needs USDINR rate
_TICKER_DEFS: dict[str, dict] = {
    # ── MCX India (INR already) ────────────────────────────────────────────
    "ALUMINIUM.MCX": {"name": "Aluminium",    "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    "COPPER.MCX":    {"name": "Copper",        "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    "NICKEL.MCX":    {"name": "Nickel",        "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    "ZINC.MCX":      {"name": "Zinc",          "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    "LEAD.MCX":      {"name": "Lead",          "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    "STEELLONG.MCX": {"name": "Steel (Long)",  "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    "GOLD.MCX":      {"name": "Gold",          "exchange": "MCX India", "raw_unit": "INR/10g",      "factor": 100.0},   # ×100 → INR/kg
    "SILVERM.MCX":   {"name": "Silver",        "exchange": "MCX India", "raw_unit": "INR/kg",       "factor": 1.0},
    # ── COMEX / LME proxy (USD) ───────────────────────────────────────────
    "HG=F":          {"name": "Copper",        "exchange": "LME (COMEX proxy)", "raw_unit": "USD/lb",      "factor": "USD_LB"},
    "ALI=F":         {"name": "Aluminium",     "exchange": "LME (COMEX proxy)", "raw_unit": "USD/MT",      "factor": "USD_MT"},
    "GC=F":          {"name": "Gold",          "exchange": "COMEX",             "raw_unit": "USD/troy oz", "factor": "USD_TROY"},
    "SI=F":          {"name": "Silver",        "exchange": "COMEX",             "raw_unit": "USD/troy oz", "factor": "USD_TROY"},
    "HRC=F":         {"name": "Steel (HRC)",   "exchange": "NYMEX",             "raw_unit": "USD/short ton", "factor": "USD_SHORT_TON"},
    # ── Exchange rate ─────────────────────────────────────────────────────
    "USDINR=X":      {"name": "USD/INR",       "exchange": "Forex",             "raw_unit": "INR/USD",     "factor": 1.0},
}

# Material type → ordered list of tickers to try (MCX first, then international)
MATERIAL_TO_TICKERS: dict[str, list[str]] = {
    "Steel":           ["HRC=F"],
    "Aluminum":        ["ALUMINIUM.MCX", "ALI=F"],
    "Copper":          ["COPPER.MCX", "HG=F"],
    "Cast Iron":       ["HRC=F"],
    "Stainless Steel": ["NICKEL.MCX"],
    "Nickel":          ["NICKEL.MCX"],
    "Zinc":            ["ZINC.MCX"],
    "Lead":            ["LEAD.MCX"],
    "Gold":            ["GOLD.MCX", "GC=F"],
    "Silver":          ["SILVERM.MCX", "SI=F"],
    "Other":           ["ALUMINIUM.MCX", "COPPER.MCX", "HRC=F"],
}


async def _yahoo_price(ticker: str, client: httpx.AsyncClient) -> Optional[float]:
    """Return latest Yahoo Finance price for ticker, using cache."""
    cached = _cache.get(ticker)
    if cached and (datetime.utcnow() - cached["at"]) < _CACHE_TTL:
        return cached["price"]

    try:
        resp = await client.get(
            f"{_YF_BASE}/{ticker}",
            params={"interval": "1d", "range": "1d"},
            headers=_YF_HEADERS,
            timeout=10.0,
            follow_redirects=True,
        )
        resp.raise_for_status()
        result = resp.json().get("chart", {}).get("result") or []
        if not result:
            return None
        meta = result[0].get("meta", {})
        price = meta.get("regularMarketPrice") or meta.get("previousClose")
        if price and price > 0:
            _cache[ticker] = {"price": float(price), "at": datetime.utcnow()}
            return float(price)
    except Exception:
        pass
    return None


def _source_url(ticker: str, exchange: str) -> str:
    if "MCX" in exchange:
        return "https://www.mcxindia.com/market-data/commodity-price"
    if ticker in ("USDINR=X",):
        return "https://finance.yahoo.com/quote/USDINR=X"
    return f"https://finance.yahoo.com/quote/{ticker}"


async def get_prices_for_material(material_type: str) -> list[dict]:
    """
    Fetch live commodity prices relevant to the given material type.
    Returns a list of dicts:
        commodity, exchange, price_inr_per_kg, source_ticker,
        source_url, fetched_at (ISO), conversion_note
    """
    tickers = MATERIAL_TO_TICKERS.get(material_type, [])
    needs_fx = any(
        _TICKER_DEFS.get(t, {}).get("factor") in ("USD_LB", "USD_TROY", "USD_SHORT_TON", "USD_MT")
        for t in tickers
    )
    print(f"DEBUG {material_type}: needs_fx = {needs_fx}")

    async with httpx.AsyncClient() as client:
        usdinr: Optional[float] = None
        if needs_fx:
            usdinr = await _yahoo_price("USDINR=X", client)
            if usdinr is None:
                usdinr = 83.50 # fallback if Yahoo Finance fails

        results = []
        for ticker in tickers:
            defn = _TICKER_DEFS.get(ticker)
            if not defn:
                continue

            raw = await _yahoo_price(ticker, client)
            if raw is None:
                continue

            factor = defn["factor"]
            if factor == "USD_LB":
                if usdinr is None:
                    continue
                price_inr = raw * 2.20462 * usdinr   # USD/lb → USD/kg → INR/kg
                note = f"Converted: {raw:.4f} USD/lb × 2.20462 × {usdinr:.2f} (USD→INR)"
            elif factor == "USD_TROY":
                if usdinr is None:
                    continue
                price_inr = (raw / 0.0311035) * usdinr  # USD/troy oz → USD/kg → INR/kg
                note = f"Converted: {raw:.2f} USD/troy oz ÷ 0.031103 × {usdinr:.2f} (USD→INR)"
            elif factor == "USD_SHORT_TON":
                if usdinr is None:
                    continue
                price_inr = (raw / 907.18474) * usdinr # USD/short ton → USD/kg → INR/kg
                note = f"Converted: {raw:.2f} USD/short ton ÷ 907.18 × {usdinr:.2f} (USD→INR)"
            elif factor == "USD_MT":
                if usdinr is None:
                    continue
                price_inr = (raw / 1000.0) * usdinr # USD/MT → USD/kg → INR/kg
                note = f"Converted: {raw:.2f} USD/MT ÷ 1000 × {usdinr:.2f} (USD→INR)"
            else:
                price_inr = raw * float(factor)
                if float(factor) != 1.0:
                    note = f"{raw:.2f} {defn['raw_unit']} × {factor} → INR/kg"
                else:
                    note = defn["raw_unit"]

            results.append({
                "commodity": defn["name"],
                "exchange": defn["exchange"],
                "price_inr_per_kg": round(price_inr, 2),
                "source_ticker": ticker,
                "source_url": _source_url(ticker, defn["exchange"]),
                "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "conversion_note": note,
            })

    return results
