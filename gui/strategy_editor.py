# gui/strategy_editor.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from utils.state import load_strategy, save_strategy, read_trade_logs

router = APIRouter()

@router.get("/strategy")
def get_strategy():
    return JSONResponse(load_strategy())

@router.post("/strategy")
async def update_strategy(request: Request):
    data = await request.json()
    strat = load_strategy()
    mode = data.get("mode", strat["mode"]).upper()
    if mode not in ["RSI_ONLY","EMA_ONLY","RSI_EMA"]:
        return JSONResponse({"error":"invalid mode"}, status_code=400)
    rsi_buy = float(data.get("rsi_buy", strat["rsi_buy"]))
    rsi_sell = float(data.get("rsi_sell", strat["rsi_sell"]))

    new_s = {"mode": mode, "rsi_buy": rsi_buy, "rsi_sell": rsi_sell}
    save_strategy(new_s)
    return JSONResponse({"ok": True, "strategy": new_s})

@router.get("/logs")
def get_logs(limit: int = 50):
    return JSONResponse({"items": read_trade_logs(limit=limit)})
