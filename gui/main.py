# gui/main.py
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .dashboard import router as dashboard_router
from .strategy_editor import router as strategy_router

# --- Unique OpenAPI operation_id generator (estää duplikaattivaroituksia) ---
def unique_id(route):
    methods = "_".join(sorted(route.methods or []))
    path = route.path.replace("/", "_")
    return f"{route.name}_{path}_{methods}"

app = FastAPI(generate_unique_id_function=unique_id)

# --- Session (tarvitaan /login) ---
# Voi asettaa RAILWAY:ssä muuttujan SESSION_SECRET; muuten fallback.
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-session-secret")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# --- Static + Templates ---
app.mount("/static", StaticFiles(directory="gui/static"), name="static")
templates = Jinja2Templates(directory="gui/templates")

# --- Routers (liitä vain kerran) ---
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(strategy_router,  prefix="/api", tags=["strategy"])

# --- Auth config ---
PASSWORD = os.getenv("DASHBOARD", os.getenv("DASHBOARD_PASSWORD", "admin"))

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, password: str = Form(...)):
    if password == PASSWORD:
        request.session["auth"] = True
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Väärä salasana"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})
