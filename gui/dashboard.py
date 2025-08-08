from fastapi import APIRouter
from utils.binance_api import get_price_data
from strategy import evaluate_signal
from utils.state import load_strategy

router = APIRouter()

@router.get("/data/{symbol}")
def get_indicator_data(symbol: str):
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

        strat = load_strategy()                 # haetaan viimeisin strategia GUI:sta
        res = evaluate_signal(closes, strat)    # sama logiikka GUI:lle ja botille
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
