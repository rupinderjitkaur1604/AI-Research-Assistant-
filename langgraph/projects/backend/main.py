from pathlib import Path


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from api.pdf_routes import router as pdf_router
from api.query_routes import router as query_router




app = FastAPI(
    title="AI Research Assistant"
)


# Current file location
BASE_DIR = Path(__file__).resolve().parent


# Project root folder
PROJECT_DIR = BASE_DIR.parent


# Frontend folder
FRONTEND_DIR = PROJECT_DIR / "frontend"


print("Project Directory:", PROJECT_DIR)
print("Frontend Directory:", FRONTEND_DIR)


# Static Files
app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR / "static")),
    name="static"
)


# Templates
templates = Jinja2Templates(
    directory=str(FRONTEND_DIR / "templates")
)


# Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):


    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )




# PDF Chat
@app.get("/pdf-chat", response_class=HTMLResponse)
async def pdf_chat(request: Request):


    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "mode": "pdf"
        }
    )




# General Chat
@app.get("/general-chat", response_class=HTMLResponse)
async def general_chat(request: Request):


    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "mode": "general"
        }
    )



app.include_router(pdf_router)
app.include_router(query_router)
