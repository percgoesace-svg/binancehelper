# main.py
import time, time as _t
from strategy import should_buy, should_sell
from utils.binance_api import client
from utils.state import append_trade_log, load_strategy

TRADE_SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","SOLUSDT",
    "ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT",
    "MATICUSDT","TRXUSDT","LTCUSDT","SHIBUSDT","UNIUSDT",
    "BCHUSDT","ATOMUSDT","XLMUSDT","NEARUSDT","FILUSDT",
    "ETCUSDT","ICPUSDT","HBARUSDT","VETUSDT","SANDUSDT",
    "EGLDUSDT","GRTUSDT","AAVEUSDT","MKRUSDT","FTMUSDT"
]

USED_USD_PERCENTAGE = 0.10
TAKE_PROFIT = 0.05
STOP_LOSS = 0.08

open_positions = {}

def get_balance_usdt():
    bal = client.get_asset_balance(asset='USDT')
    return float(bal['free']) if bal else 0.0

def place_order(symbol, side, quantity, price=None, note=None):
    # MOCK-tilaus – tulosta ja logita
    ts = int(_t.time())
    print(f"[ORDER MOCK] {side} {symbol} x {quantity} @ {price or '?'}")
    append_trade_log({
        "ts": ts,
        "side": side,
        "symbol": symbol,
        "qty": quantity,
        "price": price,
        "note": note,
    })
    # Oikea tilaus: avaa kun haluat
    # client.create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)

def check_positions():
    for symbol in list(open_positions.keys()):
        entry = open_positions[symbol]["entry"]
        qty = open_positions[symbol]["qty"]
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        pnl = (price - entry) / entry
        if pnl >= TAKE_PROFIT:
            place_order(symbol, "SELL", qty, price, note=f"TP {TAKE_PROFIT*100:.0f}%")
            del open_positions[symbol]
        elif pnl <= -STOP_LOSS:
            place_order(symbol, "SELL", qty, price, note=f"SL {STOP_LOSS*100:.0f}%")
            del open_positions[symbol]

def run_bot():
    print("Bot loop running. (Mock orders)")
    while True:
        # dynaamiset asetukset (voit muuttaa GUI:sta lennossa)
        strat = load_strategy()

        check_positions()
        balance = get_balance_usdt()
        amount_to_use = balance * USED_USD_PERCENTAGE

        for symbol in TRADE_SYMBOLS:
            if symbol in open_positions:
                continue

            klines = client.get_klines(symbol=symbol, interval="1h", limit=200)
            closes = [float(c[4]) for c in klines]
            if len(closes) < 50:
                continue

            price = closes[-1]
            if should_buy(closes):
                qty = round((amount_to_use / price), 5) if price > 0 else 0
                if qty <= 0: 
                    continue
                place_order(symbol, "BUY", qty, price, note=strat)
                open_positions[symbol] = {"entry": price, "qty": qty}
            elif should_sell(closes):
                # Ei avointa positiota: pelkkä signaali
                append_trade_log({
                    "ts": int(_t.time()),
                    "side": "SELL_SIGNAL",
                    "symbol": symbol,
                    "qty": 0,
                    "price": price,
                    "note": strat
                })

        time.sleep(60)

if __name__ == "__main__":
    run_bot()
