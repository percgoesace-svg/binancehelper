from typing import Optional
from fastapi import APIRouter, Query
from utils.binance_api import get_price_data
from strategy import evaluate_signal
from utils.state import load_strategy, get_trading_pairs, set_trading_pairs
from utils.new_listings import get_newlisting_usdt_pairs

router = APIRouter()

# --- DEBUG (piilotettu /docsista) -------------------------------------------
@router.get(
    "/_debug/pairs",                 # vaihdettu polku -> vähentää törmäysriskiä
    include_in_schema=False,
    name="debug_pairs_state_v2",     # uniikki nimi
    operation_id="debug_pairs_v2",   # uniikki operation_id
)
def debug_pairs_state_v2():
    from utils.state import TRADING_PAIRS_FILE, DATA_DIR
    pairs = get_trading_pairs()
    return {
        "count": len(pairs),
        "pairs": pairs,
        "data_dir": str(DATA_DIR),
        "file_exists": TRADING_PAIRS_FILE.exists(),
    }

# --- TRADING PAIRS -----------------------------------------------------------
@router.get(
    "/trading_pairs",
    tags=["dashboard"],
    name="trading_pairs_list_v2",     # uniikki nimi
    operation_id="trading_pairs_v2",  # uniikki operation_id
)
def trading_pairs_list_v2(force: Optional[str] = Query(default=None)):
    """
    Return trading pairs for Now Trading.

    Priority:
    1) If force=fallback -> return static fallback immediately (never empty).
    2) Try fresh Binance CMS (New Listings), persist to state if non-empty.
    3) Try existing state.
    4) Static fallback (never empty).
    """
    fallback = [
        "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","SOLUSDT",
        "ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT",
        "MATICUSDT","TRXUSDT","LTCUSDT","SHIBUSDT","UNIUSDT",
        "BCHUSDT","ATOMUSDT","XLMUSDT","NEARUSDT","FILUSDT",
        "ETCUSDT","ICPUSDT","HBARUSDT","VETUSDT","SANDUSDT",
        "EGLDUSDT","GRTUSDT","AAVEUSDT","MKRUSDT","FTMUSDT"
    ]

    # 1) Manuaalinen hätäkytkin
    if force == "fallback":
        set_trading_pairs(fallback)
        print("[/trading_pairs] forced fallback -> 30 symbols")
        return {"pairs": fallback}

    # 2) Tuore lista Binancen CMS:stä
    try:
        fresh = get_newlisting_usdt_pairs(limit=30) or []
    except Exception as e:
        print(f"[/trading_pairs] CMS fetch failed: {e}")
        fresh = []

    if fresh:
        set_trading_pairs(fresh)
        print(f"[/trading_pairs] CMS ok -> {len(fresh)} symbols")
        return {"pairs": fresh}

    # 3) Olemassa oleva state
    pairs = get_trading_pairs() or []
    if pairs:
        print(f"[/trading_pairs] state ok -> {len(pairs)} symbols")
        return {"pairs": pairs}

    # 4) Fallback (ei koskaan tyhjä)
    set_trading_pairs(fallback)
    print("[/trading_pairs] using static fallback -> 30 symbols")
    return {"pairs": fallback}

# --- INDICATOR DATA ----------------------------------------------------------
@router.get(
    "/data/{symbol}",
    tags=["dashboard"],
    name="indicator_data_v2",          # uniikki nimi
    operation_id="indicator_data_v2",  # uniikki operation_id
)
def get_indicator_data_v2(symbol: str):
    """
    Return RSI/EMA9/EMA20 + signal using the same evaluate_signal logic as the bot.
    """
    try:
        closes = get_price_data(symbol, interval='1h', limit=200)
        if not closes or len(closes) < 20:
            return {
                "symbol": symbol,
                "rsi": None,
                "ema9": None,
                "ema20": None,
                "signal": "N/A",
                "error": "not enough data",
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

