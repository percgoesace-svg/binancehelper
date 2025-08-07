# Binance API interactions
from binance.client import Client
import os

# API-avaimet .env:stä tai Railwayn ympäristömuuttujista
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Luo asiakas
client = Client(API_KEY, API_SECRET)

def get_price_data(symbol: str, interval='1h', limit=100):
    """
    Hakee sulkuhinnat Binance-kaupankäyntiparille.

    :param symbol: Esim. 'BTCUSDT'
    :param interval: Esim. '1h' tai '15m'
    :param limit: Montako kynttilää haetaan (max 1000)
    :return: Lista sulkuhinnoista (float)
    """
    candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    closes = [float(candle[4]) for candle in candles]
    return closes
