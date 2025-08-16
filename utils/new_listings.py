# utils/new_listings.py
import os
import re
import requests
from typing import List
from utils.binance_api import client

# Binance CMS API (New Listings -kategoria)
CMS_URLS = [
    "https://www.binance.com/bapi/composite/v1/public/cms/article/list?pageSize=100&pageNo=1&categoryCode=listing",
    "https://www.binance.com/bapi/composite/v1/public/cms/article/list?pageSize=100&pageNo=1&categoryCode=new_crypto_listing",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

SYMBOL_RE = re.compile(r"\(([A-Z0-9]{2,15})\)")

def _fetch_listing_titles() -> List[str]:
    for url in CMS_URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.ok:
                data = r.json()
                items = (data.get("data") or {}).get("articles") or []
                titles = [it.get("title") for it in items if it]
                if titles:
                    return titles
        except Exception:
            continue
    return []

def _extract_tickers_from_titles(titles: List[str]) -> List[str]:
    out = []
    for t in titles:
        m = SYMBOL_RE.search(t or "")
        if m:
            out.append(m.group(1))
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq

def _filter_spot_pairs_for_quote(tickers: List[str], quote: str) -> List[str]:
    try:
        info = client.get_exchange_info()
        meta = {s["symbol"]: s for s in info.get("symbols", [])}
    except Exception:
        return []
    out = []
    q = quote.upper()
    for tk in tickers:
        pair = f"{tk}{q}"
        s = meta.get(pair)
        if s and s.get("status") == "TRADING" and s.get("isSpotTradingAllowed", True):
            out.append(pair)
    return out

def get_newlisting_pairs(quote: str = "USDT", limit: int = 30) -> List[str]:
    """Palauttaa uudet listaukset muodossa BASE+QUOTE (esim. USDC)."""
    titles = _fetch_listing_titles()
    tickers = _extract_tickers_from_titles(titles)
    pairs = _filter_spot_pairs_for_quote(tickers, quote)
    return pairs[:limit]

# Yhteensopivuus vanhan nimen kanssa
def get_newlisting_usdt_pairs(limit: int = 30) -> List[str]:
    return get_newlisting_pairs("USDT", limit=limit)
