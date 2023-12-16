import asyncio
import json
import os
import warnings
from datetime import datetime
from typing import AsyncIterator

from httpx import AsyncClient

import pytest
import pytest_asyncio
from sqlalchemy import insert, text

from app.config import settings
from app.database import async_session_maker, engine
from app.models.base import Base
from app.models.template import TemplateFieldType
from app.main import app

# from fastapi.testclient import TestClient
# from httpx import AsyncClient


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

    async with async_session_maker() as session:
        for Model, values, table_name in [
            (TemplateFieldType, template_field_types, "field_type"),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)
            await session.execute(
                text(
                    f"SELECT SETVAL('{table_name}_id_seq', COALESCE((SELECT MAX(id) FROM {table_name}),1));"
                )
            )
        await session.commit()

    # yield
    # удаление всех таблиц после тестов в БД
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


# SETUP
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
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


# loop = asyncio.get_event_loop_policy().new_event_loop()
# with warnings.catch_warnings(record=True) as catched_warnings:
#     yield loop
#     # Collecting garbage should trigger warning for non-awaited coroutines
#     # gc.collect()

# for w in catched_warnings:
#     if isinstance(w.message, RuntimeWarning) and str(w.message).endswith(
#         "was never awaited"
#     ):
#         pass  # raise w.message
#     else:
#         warnings.showwarning(w.message, w.category, w.filename, w.lineno)

# # loop.close()


# Фикстура асинхронного клиента для каждого из тестов
@pytest.fixture(scope="function")
async def ac() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Фикстура аутентифицированного клиента для каждого из тестов
# @pytest.fixture(scope="session")
# async def authenticated_ac() -> AsyncIterator[AsyncClient]:
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         await ac.post(
#             "/auth/login",
#             json={"email": "test@test.com", "password": "test"},
#         )
#         assert ac.cookies["templates_access_token"]
#         yield ac
#     # await ac.close()
