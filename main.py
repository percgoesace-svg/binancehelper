import time
from strategy import should_buy, should_sell
from utils.binance_api import client
from dotenv import load_dotenv
from utils.state import get_trading_pairs, set_trading_pairs
from utils.new_listings import get_newlisting_usdt_pairs

load_dotenv()

TRADE_SYMBOLS = get_trading_pairs() or []
if not TRADE_SYMBOLS:
    try:
        TRADE_SYMBOLS = get_newlisting_usdt_pairs(limit=30) or []
    except Exception:
        TRADE_SYMBOLS = []
    if TRADE_SYMBOLS:
        set_trading_pairs(TRADE_SYMBOLS)

print(f"Using TRADE_SYMBOLS (newListing): {TRADE_SYMBOLS}")

USED_USD_PERCENTAGE = 0.1
TAKE_PROFIT = 0.05
STOP_LOSS = 0.08

open_positions = {}


def get_balance_usdt():
    balance = client.get_asset_balance(asset="USDT")
    return float(balance["free"])


def place_order(symbol, side, quantity):
    print(f"[ORDER] {side} {symbol} x {quantity}")
    # client.create_order(...)


def check_positions():
    for symbol in list(open_positions):
        entry_price = open_positions[symbol]["entry"]
        quantity = open_positions[symbol]["qty"]
        order = client.get_symbol_ticker(symbol=symbol)
        current_price = float(order['price'])

        pnl = (current_price - entry_price) / entry_price
        if pnl >= TAKE_PROFIT:
            print(f"[TP HIT] Selling {symbol} with +{pnl*100:.2f}%")
            place_order(symbol, "SELL", quantity)
            del open_positions[symbol]
        elif pnl <= -STOP_LOSS:
            print(f"[SL HIT] Selling {symbol} with {pnl*100:.2f}%")
            place_order(symbol, "SELL", quantity)
            del open_positions[symbol]


def run_bot():
    while True:
        check_positions()
        balance = get_balance_usdt()
        amount_to_use = balance * USED_USD_PERCENTAGE

        for symbol in TRADE_SYMBOLS:
            if symbol in open_positions:
                continue

            closes = [float(c[4]) for c in client.get_klines(symbol=symbol, interval="1h", limit=100)]
            if should_buy(closes):
                price = closes[-1]
                quantity = round(amount_to_use / price, 5)
                place_order(symbol, "BUY", quantity)
                open_positions[symbol] = {"entry": price, "qty": quantity}
            elif should_sell(closes):
                print(f"[Signal] {symbol}: Sell signal detected.")

        time.sleep(60 * 5)


if __name__ == "__main__":
    print("🔁 Bot is starting...")
    run_bot()
