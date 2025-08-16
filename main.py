# main.py
import time, time as _t, traceback
from strategy import evaluate_signal
from utils.binance_api import client, get_price
from utils.state import append_trade_log, load_strategy, get_trading_pairs, set_trading_pairs
from utils.new_listings import get_newlisting_usdt_pairs

# Resolve trading pairs: state -> CMS -> fallback
TRADE_SYMBOLS = get_trading_pairs() or []
if not TRADE_SYMBOLS:
    try:
        TRADE_SYMBOLS = get_newlisting_usdt_pairs(limit=30) or []
    except Exception:
        TRADE_SYMBOLS = []
if not TRADE_SYMBOLS:
    TRADE_SYMBOLS = [
        "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","SOLUSDT",
        "ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT",
        "MATICUSDT","TRXUSDT","LTCUSDT","SHIBUSDT","UNIUSDT",
        "BCHUSDT","ATOMUSDT","XLMUSDT","NEARUSDT","FILUSDT",
        "ETCUSDT","ICPUSDT","HBARUSDT","VETUSDT","SANDUSDT",
        "EGLDUSDT","GRTUSDT","AAVEUSDT","MKRUSDT","FTMUSDT"
    ]

set_trading_pairs(TRADE_SYMBOLS)
print(f"Using TRADE_SYMBOLS (newListing/fallback): {TRADE_SYMBOLS}")

USED_USD_PERCENTAGE = 0.10
TAKE_PROFIT = 0.05
STOP_LOSS = 0.08

open_positions = {}

def get_balance_usdt():
    """Palauta USDT-saldo; jos SDK-asiakas puuttuu, palauta 0 (mock-tila)."""
    try:
        if client is None:
            return 0.0
        bal = client.get_asset_balance(asset='USDT')
        return float(bal['free']) if bal else 0.0
    except Exception as e:
        print(f"[get_balance_usdt] failed: {e}")
        return 0.0

def place_order(symbol, side, quantity, price=None, note=None):
    # MOCK order – print and log
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
    # Oikea kaupankäynti: poista kommentti kun haluat
    # client.create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)

def check_positions():
    """TP/SL julkisella hinnalla (ei vaadi API keytä)."""
    strat = load_strategy()
    for symbol in list(open_positions.keys()):
        entry = open_positions[symbol]["entry"]
        qty = open_positions[symbol]["qty"]
        price = get_price(symbol)
        if price is None:
            print(f"[check_positions] price unavailable for {symbol}")
            continue

        pnl = (price - entry) / entry
        if pnl >= TAKE_PROFIT:
            place_order(symbol, "SELL", qty, price, note=f"TP {TAKE_PROFIT*100:.0f}% | {strat}")
            del open_positions[symbol]
        elif pnl <= -STOP_LOSS:
            place_order(symbol, "SELL", qty, price, note=f"SL {STOP_LOSS*100:.0f}% | {strat}")
            del open_positions[symbol]

def run_bot():
    print("Bot loop running. (Mock orders)")
    backoff = 5
    while True:
        try:
            strat = load_strategy()
            check_positions()

            balance = get_balance_usdt()
            amount_to_use = balance * USED_USD_PERCENTAGE

            from utils.binance_api import _http_get_klines  # julkinen klines
            for symbol in TRADE_SYMBOLS:
                if symbol in open_positions:
                    continue

                try:
                    klines = _http_get_klines(symbol, "1h", 200)
                    closes = [float(c[4]) for c in klines]
                except Exception as e:
                    print(f"[run_bot] klines failed for {symbol}: {e}")
                    continue

                if len(closes) < 50:
                    continue

                price = closes[-1]
                sig = evaluate_signal(closes, strat=strat)
                if sig["signal"] == "BUY":
                    qty = round((amount_to_use / price), 5) if price > 0 else 0
                    if qty <= 0:
                        continue
                    place_order(symbol, "BUY", qty, price, note=sig)
                    open_positions[symbol] = {"entry": price, "qty": qty}
                elif sig["signal"] == "SELL":
                    append_trade_log({
                        "ts": int(_t.time()),
                        "side": "SELL_SIGNAL",
                        "symbol": symbol,
                        "qty": 0,
                        "price": price,
                        "note": sig
                    })

            # success -> resetoi backoff
            backoff = 5
            time.sleep(600)  # 10 min
        except Exception as e:
            print("[run_bot] loop error:", e)
            traceback.print_exc()
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)  # max 60s

if __name__ == "__main__":
    run_bot()
