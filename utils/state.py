# utils/state.py
import json, threading
from pathlib import Path
from typing import List, Dict, Any

# 👉 aina repojuuri /app eikä sattumavarainen cwd
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

STRATEGY_FILE = DATA_DIR / "strategy.json"
TRADES_LOG = DATA_DIR / "trades.log"
TRADING_PAIRS_FILE = DATA_DIR / "trading_pairs.json"

_lock = threading.Lock()

DEFAULT_STRATEGY: Dict[str, Any] = {"mode":"RSI_EMA","rsi_buy":37,"rsi_sell":70}

def load_strategy() -> Dict[str, Any]:
    with _lock:
        if STRATEGY_FILE.exists():
            try:
                d = json.loads(STRATEGY_FILE.read_text())
                if isinstance(d, dict):
                    out = DEFAULT_STRATEGY.copy()
                    out.update(d)
                    return out
            except Exception:
                pass
        save_strategy(DEFAULT_STRATEGY.copy())
        return DEFAULT_STRATEGY.copy()

def save_strategy(s: Dict[str, Any]) -> None:
    with _lock:
        STRATEGY_FILE.write_text(json.dumps(s))

def append_trade_log(entry: Dict[str, Any]) -> None:
    with _lock:
        with TRADES_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

def read_trade_logs(limit: int = 100):
    if not TRADES_LOG.exists():
        return []
    with _lock:
        lines = TRADES_LOG.read_text(encoding="utf-8").splitlines()[-limit:]
    out=[]
    for ln in lines:
        try: out.append(json.loads(ln))
        except Exception: pass
    return out

def set_trading_pairs(pairs: List[str]) -> None:
    with _lock:
        TRADING_PAIRS_FILE.write_text(json.dumps({"pairs": pairs}))

def get_trading_pairs() -> List[str]:
    if not TRADING_PAIRS_FILE.exists():
        return []
    try:
        data = json.loads(TRADING_PAIRS_FILE.read_text())
        pairs = data.get("pairs", [])
        return [str(x) for x in pairs] if isinstance(pairs, list) else []
    except Exception:
        return []


