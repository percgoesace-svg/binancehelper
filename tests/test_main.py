import types
import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Stub out binance client to avoid network calls during import
class _ClientStub:
    def __init__(self, *args, **kwargs):
        pass
    def get_asset_balance(self, asset):
        return {"free": "0"}

client_module = types.ModuleType("client")
client_module.Client = _ClientStub
binance_module = types.ModuleType("binance")
binance_module.client = client_module
sys.modules.setdefault("binance", binance_module)
sys.modules.setdefault("binance.client", client_module)

import main

class DummyClient:
    def __init__(self):
        self.asset = None
    def get_asset_balance(self, asset):
        self.asset = asset
        return {"free": "100"}


def test_get_balance_usdt(monkeypatch):
    dummy = DummyClient()
    monkeypatch.setattr(main, "client", dummy)
    balance = main.get_balance_usdt()
    assert balance == 100.0
    assert dummy.asset == "USDT"
