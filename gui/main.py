# gui/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .dashboard import router as dashboard_router
from .strategy_editor import router as strategy_router
import os

from .dashboard import router as dashboard_router
from .strategy_editor import router as strategy_router

app = FastAPI()

app.include_router(dashboard_router, prefix="/api")
app.include_router(strategy_router, prefix="/api")

app.mount("/static", StaticFiles(directory="gui/static"), name="static")
templates = Jinja2Templates(directory="gui/templates")

PASSWORD = os.getenv("DASHBOARD_PASSWORD", "admin")

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == PASSWORD:
        resp = RedirectResponse("/dashboard", status_code=302)
        resp.set_cookie("auth", "true", httponly=True, samesite="lax")
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "error": "Väärä salasana"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if request.cookies.get("auth") != "true":
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(strategy_router, prefix="/api", tags=["strategy"])
