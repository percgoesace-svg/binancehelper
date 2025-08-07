# FastAPI app with dashboard
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os

# Luo FastAPI-sovellus
app = FastAPI()

# Lisää session middleware (jos käytät salasanasuojausta)
app.add_middleware(SessionMiddleware, secret_key="supersecret")

# Polku templaatteihin ja staattisiin tiedostoihin
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="gui/templates")

# Autentikointi (yksinkertainen salasanasuojaus)
PASSWORD = os.getenv("DASHBOARD_PASSWORD", "admin")

def require_login(request: Request):
    if request.session.get("logged_in") != True:
        raise HTTPException(status_code=403, detail="Not authenticated")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("logged_in"):
        return templates.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request):
    form = await request.form()
    if form.get("password") == PASSWORD:
        request.session["logged_in"] = True
        return templates.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("login.html", {"request": request, "error": "Väärä salasana"})

@app.get("/logout")
async def logout(request: Request):
    request.session["logged_in"] = False
    return templates.TemplateResponse("login.html", {"request": request})

# TODO: Lisää API-reitit RSI-, EMA- ja coin-dataa varten tähän

# Käynnistys Railway-yhteensopivasti
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("gui.main:app", host="0.0.0.0", port=port, reload=False)
