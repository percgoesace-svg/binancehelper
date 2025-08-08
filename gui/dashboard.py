from fastapi import APIRouter
from utils.indicators import calculate_rsi, calculate_ema
from utils.binance_api import get_price_data

router = APIRouter()

@router.get("/data/{symbol}")
def get_indicator_data(symbol: str):
    closes = get_price_data(symbol)

    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, window=9)
    ema20 = calculate_ema(closes, window=20)

    latest_rsi = round(rsi[-1], 2)
    signal = "HOLD"
    if latest_rsi < 37:
        signal = "BUY"
    elif latest_rsi > 70:
        signal = "SELL"

    return {
        "symbol": symbol,
        "rsi": latest_rsi,
        "ema9": round(ema9[-1], 2),
        "ema20": round(ema20[-1], 2),
        "signal": signal
    }
