# utils/state.py
import json
import threading
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

STRATEGY_FILE = DATA_DIR / "strategy.json"
TRADES_LOG = DATA_DIR / "trades.log"
TRADING_PAIRS_FILE = DATA_DIR / "trading_pairs.json"

_lock = threading.Lock()

DEFAULT_STRATEGY: Dict[str, Any] = {
    "mode": "RSI_EMA",   # RSI_ONLY | EMA_ONLY | RSI_EMA
    "rsi_buy": 37,
    "rsi_sell": 70,
}

# ---- Strategy (GET/SET) -----------------------------------------------------

def load_strategy() -> Dict[str, Any]:
    with _lock:
        if STRATEGY_FILE.exists():
            try:
                data = json.loads(STRATEGY_FILE.read_text())
                if not isinstance(data, dict):
                    raise ValueError("strategy.json not a dict")
                # yhdistä oletukset + tallennettu
                merged = DEFAULT_STRATEGY.copy()
                merged.update(data)
                return merged
            except Exception:
                pass
        # jos ei ole tai korruptoitunut -> kirjoita oletus
        save_strategy(DEFAULT_STRATEGY.copy())
        return DEFAULT_STRATEGY.copy()

def save_strategy(s: Dict[str, Any]) -> None:
    with _lock:
        STRATEGY_FILE.write_text(json.dumps(s))

# ---- Trades log (append/read) -----------------------------------------------

def append_trade_log(entry: Dict[str, Any]) -> None:
    """Kirjaa kauppa JSONL-muotoon."""
    line = json.dumps(entry)
    with _lock:
        with TRADES_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

def read_trade_logs(limit: int = 100) -> List[Dict[str, Any]]:
    if not TRADES_LOG.exists():
        return []
    with _lock:
        lines = TRADES_LOG.read_text(encoding="utf-8").splitlines()[-limit:]
    out: List[Dict[str, Any]] = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out

# ---- Trading pairs (set/get) ------------------------------------------------

def set_trading_pairs(pairs: List[str]) -> None:
    """Tallenna botin käyttämät parit GUI:lle luettavaksi."""
    with _lock:
        TRADING_PAIRS_FILE.write_text(json.dumps({"pairs": pairs}))

def get_trading_pairs() -> List[str]:
    """Lue botin käyttämät parit GUI:ta varten. Palauttaa [] jos ei saatavilla."""
    if not TRADING_PAIRS_FILE.exists():
        return []
    try:
        data = json.loads(TRADING_PAIRS_FILE.read_text())
        pairs = data.get("pairs", [])
        if isinstance(pairs, list):
            # varmista että str-lista
            return [str(x) for x in pairs]
    except Exception:
        pass
    return []

