from typing import Generic, Optional, TypeVar

from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Result

from app.database import async_session_maker

T = TypeVar("T")


class BaseDAO(Generic[T]):
    model: T = None

    @classmethod
    async def find_by_id(cls, model_id: int) -> Optional[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Optional[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by) -> list[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result: Result = await session.execute(query)
            return result.scalars().all()

    # @classmethod
    # async def add(cls, **data) -> None:
    #     async with async_session_maker() as session:
    #         stmt = insert(cls.model).values(**data).returning(cls.model)
    #         result = await session.execute(stmt)
    #         await session.commit()
    #         return result.scalar()
