from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import Sequence, delete, insert, select, update
from sqlalchemy.engine import Result

from app.database import async_session_maker
from app.models.base import pk_type

T = TypeVar("T")


class BaseDAO(Generic[T]):
    model: T = None

    @classmethod
    async def get_by_id(cls, id: pk_type) -> Optional[T]:
        """Получить объект с заданным идентификатором.

        Args:
            id (pk_type): идентификатор запрашиваемого объекта.

        Returns:
            Model | None: объект с заданным id.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=id)
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> Optional[T]:
        """Получить один объект по заданному фильтру.

        Args:
            filter_by (dict): параметры для поиска объекта.

        Returns:
            Model | None: объект удовлетворяющий фильтру поиска.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, **filter_by) -> Sequence[T]:
        """Получить все объекты по заданному фильтру.

        Args:
            filter_by (dict): параметры для поиска объектов.

        Returns:
            list(Model): список объектов, удовлетворяющих фильтру поиска.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result: Result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def create(cls, **data) -> Optional[T]:
        """Создать новый объект.

        Args:
            **data: значения полей создаваемого объекта.

        Returns:
            Model: созданный объект.
        """
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

    @classmethod
    async def create_list(cls, data: list[dict[str, Any]]) -> Sequence[T]:
        """Создать список новых объектов.

        Args:
            data (dict[str, Any]): список значений создаваемых объектов.

        Returns:
            list[Model]: список созданных объектов.
        """
        async with async_session_maker() as session:
            objects = [cls.model(**item) for item in data]
            session.add_all(objects)
            await session.commit()
            return objects

    @classmethod
    async def update_(cls, id: pk_type, **data) -> Optional[T]:
        """Обновить значения объекта с заданным идентификатором.

        Args:
            id (pk_type): идентификатор модифицируемого объекта.
            data: значения модифицируемых параметров.

        Returns:
            Model: модифицированный объект.
        """
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
    async def delete_(cls, id: pk_type) -> None:
        """Удалить объект с заданным идентификатором.

        Args:
            id (pk_type): идентификатор удаляемого объекта.

        Returns: None
        """
        async with async_session_maker() as session:
            stmt = delete(cls.model).where(cls.model.id == id)
            await session.execute(stmt)
            await session.commit()
