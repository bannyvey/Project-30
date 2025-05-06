from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CreateRecipe(BaseModel):
    title: str
    cooking_time: int
    ingredient_list: List[str]
    description: Optional[str]


class RecipeFullInfo(BaseModel):
    id: int
    title: str
    cooking_time: int
    ingredient_list: List[str]
    description: Optional[str]
    views: int

    model_config = ConfigDict(from_attributes=True)


class RecipeSummary(BaseModel):
    title: str
    cooking_time: int
    views: int

    model_config = ConfigDict(from_attributes=True)


class ResponseMenu(BaseModel):
    recipes: List[RecipeSummary]
