# utils/new_listings.py
import re
import requests
from typing import List
from utils.binance_api import client

CMS_URLS = [
    "https://www.binance.com/bapi/composite/v1/public/cms/article/list?pageSize=100&pageNo=1&categoryCode=listing",
    "https://www.binance.com/bapi/composite/v1/public/cms/article/list?pageSize=100&pageNo=1&categoryCode=new_crypto_listing",
]
SYMBOL_RE = re.compile(r"\(([A-Z0-9]{2,15})\)")


def _fetch_listing_titles() -> List[str]:
    for url in CMS_URLS:
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            items = (data.get("data") or {}).get("articles") or []
            titles = [it.get("title") for it in items if it]
            if titles:
                return titles
    return []


def _extract_tickers(titles: List[str]) -> List[str]:
    out, seen = [], set()
    for t in titles:
        m = SYMBOL_RE.search(t or "")
        if m:
            tk = m.group(1)
            if tk not in seen:
                seen.add(tk)
                out.append(tk)
    return out


def _filter_usdt_spot(tickers: List[str]) -> List[str]:
    info = client.get_exchange_info()
    meta = {s["symbol"]: s for s in info.get("symbols", [])}
    out = []
    for tk in tickers:
        pair = f"{tk}USDT"
        s = meta.get(pair)
        if s and s.get("status") == "TRADING" and s.get("isSpotTradingAllowed", True):
            out.append(pair)
    return out


def get_newlisting_usdt_pairs(limit: int = 30) -> List[str]:
    titles = _fetch_listing_titles()
    tickers = _extract_tickers(titles)
    pairs = _filter_usdt_spot(tickers)
    return pairs[:limit]
