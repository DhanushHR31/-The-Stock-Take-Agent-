
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .api import stock_take, adjustment
from . import web
from .models.models import Base
from .db import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (for SQLite dev use)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Ganana - Stock Take Agent", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="ganana/app/static"), name="static")
templates = Jinja2Templates(directory="ganana/app/templates")

app.include_router(stock_take.router)
app.include_router(adjustment.router)
app.include_router(web.router)
