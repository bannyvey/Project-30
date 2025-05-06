from contextlib import asynccontextmanager

from database import Base, engine
from fastapi import FastAPI
from routers import book_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(book_router.br, prefix="/recipes", tags=["recipes"])
