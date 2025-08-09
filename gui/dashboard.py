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
    Return bot trading pairs (Now Trading). If state is empty (bot not yet wrote),
    fetch directly from Binance CMS (New Listings) and persist to state.
    """
    pairs = get_trading_pairs() or []
    if not pairs:
        try:
            pairs = get_newlisting_usdt_pairs(limit=30) or []
        except Exception:
            pairs = []
        if pairs:
            set_trading_pairs(pairs)
    return {"pairs": pairs}

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

