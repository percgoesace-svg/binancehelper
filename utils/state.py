from pathlib import Path
import json
from typing import List

# Determine absolute data directory relative to this file
DATA_DIR = (Path(__file__).resolve().parent.parent / "data").resolve()
TRADING_PAIRS_FILE = DATA_DIR / "trading_pairs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_trading_pairs() -> List[str]:
    if TRADING_PAIRS_FILE.exists():
        try:
            return json.loads(TRADING_PAIRS_FILE.read_text())
        except Exception:
            return []
    return []


def set_trading_pairs(pairs: List[str]) -> None:
    TRADING_PAIRS_FILE.write_text(json.dumps(pairs))
