from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, JSON

from database import Base


class CookBook(Base):
    __tablename__ = 'cookbook'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(nullable=False)
    cooking_time: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredient_list: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str]
    views: Mapped[int] = mapped_column(Integer, default=0)