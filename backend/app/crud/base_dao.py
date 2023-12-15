from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import Sequence, delete, insert, select, update
from sqlalchemy.engine import Result

from app.database import async_session_maker

T = TypeVar("T")


class BaseDAO(Generic[T]):
    model: T = None

    @classmethod
    async def get_by_id(cls, model_id: int) -> Optional[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> Optional[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, **filter_by) -> Sequence[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result: Result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def create(cls, **data) -> Optional[T]:
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

    @classmethod
    async def create_list(cls, data: list[dict[str, Any]]) -> Sequence[T]:
        async with async_session_maker() as session:
            objects = [cls.model(**item) for item in data]
            session.add_all(objects)
            await session.commit()
            return objects

    @classmethod
    async def update_(cls, id: int, **data) -> Optional[T]:
        async with async_session_maker() as session:
            stmt = (
                update(cls.model)
                .where(cls.model.id == id)
                .values(**data)
                .returning(cls.model)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

    @classmethod
    async def delete_(cls, id: int) -> None:
        async with async_session_maker() as session:
            stmt = delete(cls.model).where(cls.model.id == id)
            await session.execute(stmt)
            await session.commit()
