import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

PATH = os.path.dirname(os.path.abspath(__file__))
PATH_TO_BD = os.path.join(PATH, "test_base.bd")

DATABASE_URL = f"sqlite+aiosqlite:///{PATH_TO_BD}"


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo=True)

async_local_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with async_local_session() as session:
        yield session
