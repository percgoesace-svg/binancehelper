from binance.client import Client
import os

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

def get_price_data(symbol: str, interval='1h', limit=100):
    candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    closes = [float(candle[4]) for candle in candles]
    return closes
