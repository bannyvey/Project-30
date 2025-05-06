import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database import get_db, Base
from main import app
from models import CookBook

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
client = TestClient(app)
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    # Создание таблиц перед тестами
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Очистка после тестов
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_get_recipes_empty():
    """Тест получения пустого списка рецептов"""
    response = client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == {"recipes":[]}

@pytest.mark.asyncio
async def test_create_recipe():
    """Тест создания рецепта"""
    recipe_data = {
        "title": "Омлет",
        "cooking_time": 10,
        "ingredient_list": ["Все знают"],
        "description": "Описание"
    }
    response = client.post("/recipes", json=recipe_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Омлет"
    assert data["cooking_time"] == 10
    assert data["ingredient_list"] == ["Все знают"]
    assert data["description"] == "Описание"
    assert data["views"] == 0
    assert "id" in data

@pytest.mark.asyncio
async def test_get_recipes_with_data():
    """Тест получения списка рецептов после добавления"""
    recipe_data_2 = {
        "title": "Паста",
        "cooking_time": 20,
        "ingredient_list": ["Спагетти 200 г", "Бекон 100 г"],
        "description": "Отварить спагетти, обжарить бекон",
        "views": 5
    }
    async with TestSessionLocal() as session:
        recipe = CookBook(**recipe_data_2)
        session.add(recipe)
        await session.commit()

    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["recipes"]) == 2
    assert data["recipes"][0]["title"] == "Паста"
    assert data["recipes"][0]["views"] == 5
    assert data["recipes"][1]["views"] == 0

@pytest.mark.asyncio
async def test_get_recipe_by_id():
    """Тест увеличения просмотра"""
    recipe_data = {
        "title": "Тестовый рецепт",
        "cooking_time": 15,
        "ingredient_list": ["Ингредиент 1", "Ингредиент 2"],
        "description": "Тестовое описание"
    }
    create_response = client.post("/recipes/", json=recipe_data)
    assert create_response.status_code == 200
    recipe_id = create_response.json()["id"]

    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recipe_id
    assert data["views"] == 1

@pytest.mark.asyncio
async def test_get_recipe_not_found():
    """Тест получения несуществующего рецепта"""
    response = client.get("/recipes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Рецепт не найден"}

@pytest.mark.asyncio
async def test_create_recipe_invalid_data():
    """Тест создания рецепта с некорректными данными"""
    invalid_data = {
        "title": "",
        "cooking_time": "десять минут",
        "ingredient_list": [],
        "description": "Тест"
    }
    response = client.post("/recipes", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()