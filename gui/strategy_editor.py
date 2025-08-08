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
    s = load_strategy()
    mode = (data.get("mode", s["mode"]) or "RSI_EMA").upper()
    if mode not in ["RSI_ONLY","EMA_ONLY","RSI_EMA"]:
        return JSONResponse({"error":"invalid mode"}, status_code=400)
    s["mode"] = mode
    if "rsi_buy" in data: s["rsi_buy"] = float(data["rsi_buy"])
    if "rsi_sell" in data: s["rsi_sell"] = float(data["rsi_sell"])
    save_strategy(s)
    return JSONResponse({"ok": True, "strategy": s})

@router.get("/logs")
def get_logs(limit: int = 100):
    return JSONResponse({"items": read_trade_logs(limit=limit)})
