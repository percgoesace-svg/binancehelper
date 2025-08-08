import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    prices = pd.Series(prices)
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(0).tolist()

def calculate_ema(prices, window=9):
    prices = pd.Series(prices)
    ema = prices.ewm(span=window, adjust=False).mean()
    return ema.tolist()
