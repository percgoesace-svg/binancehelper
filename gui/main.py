from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gui.dashboard import router as dashboard_router
from gui.strategy_editor import router as strategy_router
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="gui/static"), name="static")

templates = Jinja2Templates(directory="gui/templates")

# Yksinkertainen salasana
PASSWORD = os.getenv("DASHBOARD_PASSWORD", "tonttu")

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, password: str = Form(...)):
    if password == PASSWORD:
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="authenticated", value="true")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Väärä salasana"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})

# API-reitit
app.include_router(dashboard_router, prefix="/api")
app.include_router(strategy_router, prefix="/api")