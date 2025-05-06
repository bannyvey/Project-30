from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.book_model import CookBook
from schemes.cookbook_scheme import (
    CreateRecipe,
    RecipeFullInfo,
    RecipeSummary,
    ResponseMenu,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

br = APIRouter()


@br.get("/", response_model=ResponseMenu, summary="Список рецептов")
async def get_recipes(session: AsyncSession = Depends(get_db)):
    try:
        result_scalar = await session.scalars(
            select(CookBook).order_by(
                CookBook.views.desc(), CookBook.cooking_time.asc()
            )
        )
        recipes = result_scalar.all()
        return ResponseMenu(
            recipes=[RecipeSummary.model_validate(recipe) for recipe in recipes]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@br.get("/{recipe_id}", response_model=RecipeFullInfo, summary="Рецепт по ID")
async def get_recipe_by_id(recipe_id: int, session: AsyncSession = Depends(get_db)):
    try:
        response = await session.get(CookBook, recipe_id)
        if not response:
            raise HTTPException(status_code=404, detail="Рецепт не найден")
        response.views += 1
        await session.commit()
        await session.refresh(response)
        return response
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат ID")


@br.post("/", response_model=RecipeFullInfo, summary="Создание нового рецепта")
async def create_recipe(request: CreateRecipe, session: AsyncSession = Depends(get_db)):
    try:
        response = request.model_dump()
        result = CookBook(**response)
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
