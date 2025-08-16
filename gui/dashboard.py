from typing import Optional
import os
from fastapi import APIRouter, Query
from utils.binance_api import get_price_data
from strategy import evaluate_signal
from utils.state import load_strategy, get_trading_pairs, set_trading_pairs
from utils.new_listings import get_newlisting_pairs

router = APIRouter()
QUOTE_ASSET = os.getenv("QUOTE_ASSET", "USDT").upper()

@router.get(
    "/_debug/pairs",
    include_in_schema=False,
    name="debug_pairs_state_v2",
    operation_id="debug_pairs_v2",
)
def debug_pairs_state_v2():
    from utils.state import TRADING_PAIRS_FILE, DATA_DIR
    pairs = get_trading_pairs()
    return {
        "count": len(pairs),
        "pairs": pairs,
        "data_dir": str(DATA_DIR),
        "file_exists": TRADING_PAIRS_FILE.exists(),
        "quote": QUOTE_ASSET,
    }

@router.get(
    "/trading_pairs",
    tags=["dashboard"],
    name="trading_pairs_list_v2",
    operation_id="trading_pairs_v2",
)
def trading_pairs_list_v2(force: Optional[str] = Query(default=None)):
    """
    1) force=fallback -> staattinen lista (ei tyhjä).
    2) Hae tuoreet New Listing -parit QUOTE_ASSET:lla ja tallenna stateen.
    3) Muussa tapauksessa lue state.
    4) Lopuksi staattinen fallback QUOTE_ASSET:lla.
    """
    fallback = [
        "BTC","ETH","BNB","XRP","SOL",
        "ADA","DOGE","AVAX","DOT","LINK",
        "MATIC","TRX","LTC","SHIB","UNI",
        "BCH","ATOM","XLM","NEAR","FIL",
        "ETC","ICP","HBAR","VET","SAND",
        "EGLD","GRT","AAVE","MKR","FTM"
    ]
    fallback = [f"{b}{QUOTE_ASSET}" for b in fallback]

    if force == "fallback":
        set_trading_pairs(fallback)
        print(f"[/trading_pairs] forced fallback -> {len(fallback)} symbols ({QUOTE_ASSET})")
        return {"pairs": fallback}

    try:
        fresh = get_newlisting_pairs(quote=QUOTE_ASSET, limit=30) or []
    except Exception as e:
        print(f"[/trading_pairs] CMS fetch failed: {e}")
        fresh = []

    if fresh:
        set_trading_pairs(fresh)
        print(f"[/trading_pairs] CMS ok -> {len(fresh)} symbols ({QUOTE_ASSET})")
        return {"pairs": fresh}

    pairs = get_trading_pairs() or []
    if pairs:
        print(f"[/trading_pairs] state ok -> {len(pairs)} symbols ({QUOTE_ASSET})")
        return {"pairs": pairs}

    set_trading_pairs(fallback)
    print(f"[/trading_pairs] using static fallback -> {len(fallback)} symbols ({QUOTE_ASSET})")
    return {"pairs": fallback}

@router.get(
    "/data/{symbol}",
    tags=["dashboard"],
    name="indicator_data_v2",
    operation_id="indicator_data_v2",
)
def get_indicator_data_v2(symbol: str):
    try:
        closes = get_price_data(symbol, interval='1h', limit=200)
        if not closes or len(closes) < 20:
            return {
                "symbol": symbol,
                "rsi": None,
                "ema9": None,
                "ema20": None,
                "signal": "N/A",
                "error": "no klines (symbol/interval?)",
            }
        strat = load_strategy()
        res = evaluate_signal(closes, strat)
        res.update({"symbol": symbol, "error": None})
        return res
    except Exception as e:
        return {
            "symbol": symbol,
            "rsi": None,
            "ema9": None,
            "ema20": None,
            "signal": "N/A",
            "error": str(e),
        }
