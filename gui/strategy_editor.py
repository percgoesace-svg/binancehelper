from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

current_strategy = {"mode": "RSI_EMA"}

@router.get("/strategy")
def get_strategy():
    return JSONResponse(content=current_strategy)

@router.post("/strategy")
async def update_strategy(request: Request):
    data = await request.json()
    mode = data.get("mode")

    if mode not in ["RSI_ONLY", "EMA_ONLY", "RSI_EMA"]:
        return JSONResponse(content={"error": "Invalid strategy mode"}, status_code=400)

    current_strategy["mode"] = mode
    return JSONResponse(content={"message": f"Strategy updated to {mode}"})