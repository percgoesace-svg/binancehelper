# strategy.py
from utils.indicators import calculate_rsi, calculate_ema
from utils.state import load_strategy

def evaluate_signal(closes, strat=None):
    """
    Palauttaa yhden totuudenlähteen: rsi, ema9, ema20, signal ('BUY'|'SELL'|'HOLD').
    strat = {"mode": "RSI_EMA"|"RSI_ONLY"|"EMA_ONLY", "rsi_buy": 37, "rsi_sell": 70}
    """
    if strat is None:
        strat = load_strategy()

    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, window=9)
    ema20 = calculate_ema(closes, window=20)

    last_rsi = rsi[-1]
    m = (strat.get("mode") or "RSI_EMA").upper()
    rsi_buy  = float(strat.get("rsi_buy", 37))
    rsi_sell = float(strat.get("rsi_sell", 70))

    buy = sell = False
    if m == "RSI_ONLY":
        buy  = last_rsi < rsi_buy
        sell = last_rsi > rsi_sell
    elif m == "EMA_ONLY":
        buy  = ema9[-1] > ema20[-1]
        sell = ema9[-1] < ema20[-1]
    else:  # RSI_EMA (default)
        buy  = (last_rsi < rsi_buy) and (ema9[-1] > ema20[-1])
        sell = (last_rsi > rsi_sell) and (ema9[-1] < ema20[-1])

    signal = "BUY" if buy else "SELL" if sell else "HOLD"
    return {
        "rsi": float(round(last_rsi, 2)),
        "ema9": float(round(ema9[-1], 2)),
        "ema20": float(round(ema20[-1], 2)),
        "signal": signal,
        "mode": m,
        "rsi_buy": rsi_buy,
        "rsi_sell": rsi_sell,
    }

# Backwards-compat: jos muualla kutsutaan näitä
def should_buy(closes):
    return evaluate_signal(closes)["signal"] == "BUY"

def should_sell(closes):
    return evaluate_signal(closes)["signal"] == "SELL"
