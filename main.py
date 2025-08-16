# main.py
import os
import time, time as _t, traceback
from strategy import evaluate_signal
from utils.binance_api import client, get_price, _http_get_klines
from utils.state import append_trade_log, load_strategy, get_trading_pairs, set_trading_pairs
from utils.new_listings import get_newlisting_pairs, get_newlisting_usdt_pairs

# --- Konfig ---
QUOTE_ASSET = os.getenv("QUOTE_ASSET", "USDT").upper()  # 🔸 ASETTAMALLA QUOTE_ASSET=USDC vaihdat USDC:hen
USED_USD_PERCENTAGE = float(os.getenv("USED_USD_PERCENTAGE", "0.10"))  # 10%
TAKE_PROFIT = float(os.getenv("TAKE_PROFIT", "0.05"))                  # 5%
STOP_LOSS   = float(os.getenv("STOP_LOSS", "0.08"))                    # 8%
# Mock-budjetti, jos oikea saldo = 0
MOCK_BUDGET = float(os.getenv("MOCK_BUDGET", os.getenv("MOCK_BUDGET_USDT", "100")))
SLEEP_SEC   = int(os.getenv("LOOP_SLEEP_SECONDS", "600"))              # 10 min

open_positions = {}

# --- Parit: state -> CMS (valittu quote) -> fallback (valittu quote) ---
TRADE_SYMBOLS = get_trading_pairs() or []
if not TRADE_SYMBOLS:
    try:
        # 🔸 hae uusimmat listaukset valitulla quotella (USDC/USDT)
        TRADE_SYMBOLS = get_newlisting_pairs(quote=QUOTE_ASSET, limit=30) or []
    except Exception:
        TRADE_SYMBOLS = []
if not TRADE_SYMBOLS:
    bases = [
        "BTC","ETH","BNB","XRP","SOL",
        "ADA","DOGE","AVAX","DOT","LINK",
        "MATIC","TRX","LTC","SHIB","UNI",
        "BCH","ATOM","XLM","NEAR","FIL",
        "ETC","ICP","HBAR","VET","SAND",
        "EGLD","GRT","AAVE","MKR","FTM"
    ]
    TRADE_SYMBOLS = [f"{b}{QUOTE_ASSET}" for b in bases]

set_trading_pairs(TRADE_SYMBOLS)
print(f"[init] Using QUOTE_ASSET={QUOTE_ASSET}, TRADE_SYMBOLS: {TRADE_SYMBOLS}")

def get_balance_quote():
    """Palauta valitun quote-assetin saldo (esim. USDC)."""
    try:
        if client is None:
            return 0.0
        bal = client.get_asset_balance(asset=QUOTE_ASSET)
        return float(bal['free']) if bal else 0.0
    except Exception as e:
        print(f"[get_balance_quote] failed: {e}")
        return 0.0

def place_order(symbol, side, quantity, price=None, note=None):
    """MOCK-tilaus: lokitetaan ja tulostetaan. (Poista kommentti alla oikeaa tilausta varten.)"""
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
    # Oikea tilaus:
    # if client is not None:
    #     client.create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)

def check_positions():
    """TP/SL julkisella hinnalla (ei vaadi API-keytä)."""
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
    print("[run_bot] Bot loop running. (Mock orders)")
    backoff = 5
    while True:
        try:
            strat = load_strategy()
            check_positions()

            real_balance = get_balance_quote()
            base_budget = real_balance if real_balance > 0 else MOCK_BUDGET
            amount_to_use = base_budget * USED_USD_PERCENTAGE

            print(f"[loop] quote={QUOTE_ASSET} balance={real_balance:.4f} base_budget={base_budget:.4f} use={amount_to_use:.4f}")

            for symbol in TRADE_SYMBOLS:
                if symbol in open_positions:
                    continue

                try:
                    klines = _http_get_klines(symbol, "1h", 200)  # julkinen klines
                    closes = [float(c[4]) for c in klines]
                except Exception as e:
                    print(f"[loop] klines failed for {symbol}: {e}")
                    continue

                if len(closes) < 50:
                    print(f"[loop] skip {symbol}: not enough candles ({len(closes)})")
                    continue

                price = closes[-1]
                sig = evaluate_signal(closes, strat=strat)
                print(f"[signal] {symbol}: {sig.get('signal')} (RSI={sig.get('rsi')}, EMA9={sig.get('ema9')}, EMA20={sig.get('ema20')})")

                if sig["signal"] == "BUY":
                    qty = round((amount_to_use / price), 5) if price > 0 else 0
                    if qty <= 0:
                        print(f"[buy-skip] {symbol}: qty<=0 (price={price}, use={amount_to_use})")
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

            backoff = 5
            time.sleep(SLEEP_SEC)
        except Exception as e:
            print("[run_bot] loop error:", e)
            traceback.print_exc()
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)

if __name__ == "__main__":
    run_bot()
