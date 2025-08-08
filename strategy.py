# strategy.py
from utils.indicators import calculate_rsi, calculate_ema
from utils.state import load_strategy

def _signals_from_mode(closes, strat):
    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, window=9)
    ema20 = calculate_ema(closes, window=20)
    last_rsi = rsi[-1]
    mode = (strat.get("mode") or "RSI_EMA").upper()
    rsi_buy = float(strat.get("rsi_buy", 37))
    rsi_sell = float(strat.get("rsi_sell", 70))

    buy = sell = False

    if mode == "RSI_ONLY":
        buy = last_rsi < rsi_buy
        sell = last_rsi > rsi_sell
    elif mode == "EMA_ONLY":
        buy = ema9[-1] > ema20[-1]
        sell = ema9[-1] < ema20[-1]
    else:  # RSI_EMA
        buy  = (last_rsi < rsi_buy) and (ema9[-1] > ema20[-1])
        sell = (last_rsi > rsi_sell) and (ema9[-1] < ema20[-1])

    return buy, sell, last_rsi, ema9[-1], ema20[-1]

def should_buy(closes):
    strat = load_strategy()
    buy, _, *_ = _signals_from_mode(closes, strat)
    return buy

def should_sell(closes):
    strat = load_strategy()
    _, sell, *_ = _signals_from_mode(closes, strat)
    return sell

