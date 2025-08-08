# utils/new_listings.py
import re
import json
import requests
from typing import List
from utils.binance_api import client

NEW_LISTING_URL = "https://www.binance.com/en/markets/newListing"

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}

def _ordered_unique(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def _fetch_newlisting_html() -> str:
    r = requests.get(NEW_LISTING_URL, headers=UA, timeout=12)
    r.raise_for_status()
    return r.text

def _extract_symbols_from_embedded_json(html: str) -> List[str]:
    """
    Monilla Binance-markkinasivuilla on upotettu 'window.__APP_DATA__ = {...}'.
    Poimitaan sieltä mahdolliset symbolit.
    """
    # Etsi iso JSON-blokki
    m = re.search(r"__APP_DATA__\s*=\s*(\{.*?\});", html, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []

    # Heuristiikka: hae kaikki "symbol":"XXXXUSDT"-esiintymät JSON-stringistä uudelleen
    # (varmin tapa, koska rakenne päivittyy usein)
    raw = m.group(1)
    found = re.findall(r'"symbol"\s*:\s*"([A-Z0-9]{2,15}USDT)"', raw)
    return _ordered_unique(found)

def _extract_symbols_from_links(html: str) -> List[str]:
    """
    Fallback: etsi linkeistä /en/trade/FOO_USDT tyyppiset osoitteet.
    Muunna FOO_USDT -> FOOUSDT.
    """
    found = []
    for m in re.finditer(r'/en/trade/([A-Z0-9]{2,15})_USDT', html):
        sym = m.group(1) + "USDT"
        found.append(sym)
    # Lisäksi joskus muoto on .../en/trade?pair=FOOUSDT tms.
    for m in re.finditer(r'pair=([A-Z0-9]{2,15}USDT)', html):
        found.append(m.group(1))
    return _ordered_unique(found)

def _filter_spot_trading_pairs(symbols: List[str]) -> List[str]:
    """
    Suodata vain ne parit, jotka löytyvät exchangeInfo:sta ja ovat TRADING.
    """
    try:
        info = client.get_exchange_info()
    except Exception:
        return []
    meta = {s["symbol"]: s for s in info.get("symbols", [])}
    out = []
    for s in symbols:
        si = meta.get(s)
        if not si:
            continue
        if si.get("status") == "TRADING" and si.get("isSpotTradingAllowed", True):
            out.append(s)
    return out

def get_newlisting_usdt_pairs(limit: int = 30) -> List[str]:
    """
    Palauta enintään 'limit' kpl uusimman newListing-sivun USDT-paria.
    """
    html = _fetch_newlisting_html()

    # 1) Yritä upotetusta JSON:sta
    syms = _extract_symbols_from_embedded_json(html)

    # 2) Fallback: linkeistä
    if not syms:
        syms = _extract_symbols_from_links(html)

    # 3) Validoi spot/TRADING
    syms = _filter_spot_trading_pairs(syms)

    # Palauta max 'limit'
    return syms[:limit]
