from fastapi import APIRouter
from utils.binance_api import get_price_data
from strategy import evaluate_signal
from utils.state import load_strategy, get_trading_pairs

router = APIRouter()

@router.get("/data/{symbol}")
def get_indicator_data(symbol: str):
    """
    Palauttaa RSI/EMA9/EMA20 + signal annetulle symbolille.
    Käyttää samaa evaluate_signal-logiikkaa kuin botti.
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

        strat = load_strategy()              # haetaan viimeisin strategia
        res = evaluate_signal(closes, strat) # sama logiikka GUI:lle ja botille
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

@router.get("/trading_pairs")
def trading_pairs():
    """
    Palauttaa listan pareista, joita botti käyttää (Now Trading -näkymää varten).
    Lista päivitetään bottikäynnistyksessä newListing-sivulta ja
    tallennetaan utils/state.py:n kautta.
    """
    pairs = get_trading_pairs() or []
    return {"pairs": pairs}
