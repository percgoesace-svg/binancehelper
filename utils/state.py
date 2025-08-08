# utils/state.py
import json, threading
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
STRATEGY_FILE = DATA_DIR / "strategy.json"
TRADES_LOG = DATA_DIR / "trades.log"

_lock = threading.Lock()

DEFAULT_STRATEGY = {"mode":"RSI_EMA","rsi_buy":37,"rsi_sell":70}

def load_strategy():
    with _lock:
        if STRATEGY_FILE.exists():
            try:
                s = json.loads(STRATEGY_FILE.read_text())
                return {**DEFAULT_STRATEGY, **s}
            except Exception:
                pass
        save_strategy(DEFAULT_STRATEGY)
        return DEFAULT_STRATEGY.copy()

def save_strategy(s: dict):
    with _lock:
        STRATEGY_FILE.write_text(json.dumps(s))

def append_trade_log(entry: dict):
    with _lock:
        with TRADES_LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")

def read_trade_logs(limit: int = 100):
    if not TRADES_LOG.exists():
        return []
    with _lock:
        lines = TRADES_LOG.read_text().splitlines()[-limit:]
    out=[]
    for ln in lines:
        try: out.append(json.loads(ln))
        except Exception: pass
    return out
