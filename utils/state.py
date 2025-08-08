# utils/state.py
import json, os, threading
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
STRATEGY_FILE = DATA_DIR / "strategy.json"
TRADES_LOG = DATA_DIR / "trades.log"

_lock = threading.Lock()

DEFAULT_STRATEGY = {
    "mode": "RSI_EMA",   # RSI_ONLY | EMA_ONLY | RSI_EMA
    "rsi_buy": 37,
    "rsi_sell": 70
}

def load_strategy():
    with _lock:
        if STRATEGY_FILE.exists():
            try:
                with open(STRATEGY_FILE, "r") as f:
                    data = json.load(f)
                    return {**DEFAULT_STRATEGY, **data}
            except Exception:
                return DEFAULT_STRATEGY.copy()
        else:
            save_strategy(DEFAULT_STRATEGY.copy())
            return DEFAULT_STRATEGY.copy()

def save_strategy(s: dict):
    with _lock:
        with open(STRATEGY_FILE, "w") as f:
            json.dump(s, f)

def append_trade_log(entry: dict):
    # JSON Lines -tyyli
    with _lock:
        with open(TRADES_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

def read_trade_logs(limit: int = 50):
    if not TRADES_LOG.exists():
        return []
    with _lock:
        lines = TRADES_LOG.read_text().splitlines()[-limit:]
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out
