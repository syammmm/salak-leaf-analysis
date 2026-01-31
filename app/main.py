from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import leaf
from app.logger import setup_logger

setup_logger()

app = FastAPI(
    title="Salak Leaf Analysis",
    description="Web-based image processing for salak leaf health",
    version="0.1.0"
)

app.include_router(leaf.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.mount("/temp", StaticFiles(directory="temp"), name="temp")

templates = Jinja2Templates(directory="app/templates")
