from fastapi import APIRouter
from utils.binance_api import get_price_data
from strategy import evaluate_signal
from utils.state import load_strategy, get_trading_pairs, set_trading_pairs
from utils.new_listings import get_newlisting_usdt_pairs

router = APIRouter()

@router.get("/debug/pairs")
def debug_pairs():
    from utils.state import TRADING_PAIRS_FILE, DATA_DIR
    pairs = get_trading_pairs()
    return {
        "count": len(pairs),
        "pairs": pairs,
        "data_dir": str(DATA_DIR),
        "file_exists": TRADING_PAIRS_FILE.exists(),
    }

@router.get("/trading_pairs")
def trading_pairs():
    """
    Always try fresh New Listing pairs first (Binance CMS).
    If that fails/empty, return state; if empty, return a static fallback.
    """
    # 1) Fresh from Binance CMS
    try:
        fresh = get_newlisting_usdt_pairs(limit=30) or []
    except Exception:
        fresh = []

    if fresh:
        set_trading_pairs(fresh)
        return {"pairs": fresh}

    # 2) Existing state
    pairs = get_trading_pairs() or []
    if pairs:
        return {"pairs": pairs}

    # 3) Fallback (never empty)
    fallback = [
        "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","SOLUSDT",
        "ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT",
        "MATICUSDT","TRXUSDT","LTCUSDT","SHIBUSDT","UNIUSDT",
        "BCHUSDT","ATOMUSDT","XLMUSDT","NEARUSDT","FILUSDT",
        "ETCUSDT","ICPUSDT","HBARUSDT","VETUSDT","SANDUSDT",
        "EGLDUSDT","GRTUSDT","AAVEUSDT","MKRUSDT","FTMUSDT"
    ]
    set_trading_pairs(fallback)
    return {"pairs": fallback}

@router.get("/data/{symbol}")
def get_indicator_data(symbol: str):
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
