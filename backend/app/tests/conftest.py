import urllib
import asyncio
import json
import os
import warnings
from datetime import datetime
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import insert, text

from app.config import settings
from app.database import async_session_maker, engine
from app.main import app
from app.models.base import Base
from app.models.template import TemplateFieldType
from app.models.user import User

# from fastapi.testclient import TestClient
# from httpx import AsyncClient

AUTH_COOKIE = "document_template_auth"


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        # удаление всех имеющихся таблице в БД
        await conn.run_sync(Base.metadata.drop_all)
        # создание всех таблиц в тестовой БД
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    template_field_types = open_mock_json("field_type")
    users = open_mock_json("user")

    async with async_session_maker() as session:
        for Model, values, table_name, init_id in [
            (TemplateFieldType, template_field_types, "field_type", True),
            (User, users, "user", False),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)
            if init_id:
                await session.execute(
                    text(
                        f"SELECT SETVAL('{table_name}_id_seq', COALESCE((SELECT MAX(id) FROM {table_name}),1));"
                    )
                )
        await session.commit()

    yield
    # удаление всех таблиц после тестов в БД
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


# SETUP
# @pytest.fixture(scope="session")
# def event_loop(request):
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="module")
def event_loop():
    # loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(1))
    loop.close()


# Взято из документации к pytest-asyncio
# @pytest.fixture(scope="session")
# def event_loop(request):
#     """Create an instance of the default event loop for each test case."""
#     # if sys.platform == "win32" and sys.version_info.minor >= 8:
#     #     asyncio.set_event_loop_policy(
#     #         asyncio.WindowsSelectorEventLoopPolicy()  # pylint: disable=no-member
#     #     )
#     # loop = asyncio.get_event_loop_policy().new_event_loop()
#     # yield loop
#     # loop.close()


# Фикстура асинхронного клиента для каждого из тестов
@pytest.fixture(autouse=True, scope="session")
async def ac() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Фикстура аутентифицированного клиента для каждого из тестов
@pytest.fixture(autouse=True, scope="session")
async def user_ac() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/login",
            data={
                "username": "user@example.com",
                "password": "user",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        jwt = ac.cookies.get(AUTH_COOKIE)
        assert jwt, "Куки авторизованного клиента не найдены"
        ac.headers["Cookie"] = f"{AUTH_COOKIE}={jwt}"
        yield ac
    # await ac.close()


# Фикстура аутентифицированного клиента суперпользователя для каждого из тестов
@pytest.fixture(autouse=True, scope="session")
async def superuser_ac() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/login",
            data={
                "username": "admin@example.com",
                "password": "admin",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        jwt = ac.cookies.get("document_template_auth")
        assert jwt, "Куки авторизованного суперпользователя не найдены"
        ac.headers["Cookie"] = f"{AUTH_COOKIE}={jwt}"
        yield ac
