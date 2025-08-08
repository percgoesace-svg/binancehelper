from utils.indicators import calculate_rsi, calculate_ema

def should_buy(closes):
    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, window=9)
    ema20 = calculate_ema(closes, window=20)

    if rsi[-1] < 37 and ema9[-1] > ema20[-1]:
        return True
    return False

def should_sell(closes):
    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, window=9)
    ema20 = calculate_ema(closes, window=20)

    if rsi[-1] > 70 and ema9[-1] < ema20[-1]:
        return True
    return False
