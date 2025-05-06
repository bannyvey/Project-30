from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers import book_router
from database import engine, Base
from models.book_model import CookBook


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(lifespan=lifespan)

app.include_router(book_router.br, prefix="/recipes", tags=["recipes"])

