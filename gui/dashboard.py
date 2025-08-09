from fastapi import APIRouter
from utils.indicators import calculate_rsi, calculate_ema
from utils.binance_api import get_price_data
from utils.state import get_trading_pairs, set_trading_pairs
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
        "file_exists": (TRADING_PAIRS_FILE.exists()),
    }

@router.get("/trading_pairs")
def trading_pairs():
    """
    Palauttaa botin käyttämät parit. Jos state on tyhjä (botti ei kirjoittanut vielä),
    hae suoraan Binancen CMS:stä ja tallenna stateen.
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
    try:
        closes = get_price_data(symbol, interval='1h', limit=200)
        if not closes or len(closes) < 20:
            return {
                "symbol": symbol, "rsi": None, "ema9": None, "ema20": None,
                "signal": "N/A", "error": "not enough data"
            }

        rsi = calculate_rsi(closes)
        ema9 = calculate_ema(closes, window=9)
        ema20 = calculate_ema(closes, window=20)

        latest_rsi = round(rsi[-1], 2)
        signal = "HOLD"
        if latest_rsi < 37 and ema9[-1] > ema20[-1]:
            signal = "BUY"
        elif latest_rsi > 70 and ema9[-1] < ema20[-1]:
            signal = "SELL"

        return {
            "symbol": symbol,
            "rsi": latest_rsi,
            "ema9": round(ema9[-1], 2),
            "ema20": round(ema20[-1], 2),
            "signal": signal,
            "error": None
        }
    except Exception as e:
        return {
            "symbol": symbol, "rsi": None, "ema9": None, "ema20": None,
            "signal": "N/A", "error": str(e)
        }
