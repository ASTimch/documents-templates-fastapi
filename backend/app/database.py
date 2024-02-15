from typing import Annotated, AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
    # DATABASE_PARAMS = {}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}  # for celery background
    # DATABASE_PARAMS = {}

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

idpk = Annotated[int, "Идентификатор объекта"]


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
