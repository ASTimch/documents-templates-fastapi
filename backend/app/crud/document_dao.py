from typing import Optional

from sqlalchemy import Result, Sequence, select
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base_dao import BaseDAO
from app.database import async_session_maker
from app.models.base import pk_type
from app.models.document import Document, DocumentField
from app.models.template import TemplateField


class DocumentFieldDAO(BaseDAO):
    model = DocumentField

    @classmethod
    async def get_by_id(cls, id: pk_type) -> Optional[DocumentField]:
        """Получить поле документа с заданным идентификатором.

        Args:
            id (pk_type): идентификатор запрашиваемого объекта.

        Returns:
            Model | None: объект с заданным id.
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id=id)
                .options(
                    joinedload(DocumentField.template_field).joinedload(
                        TemplateField.type
                    )
                )
            )
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> Optional[DocumentField]:
        """Получить один объект по заданному фильтру.

        Args:
            filter_by (dict): параметры для поиска объекта.

        Returns:
            Model | None: объект удовлетворяющий фильтру поиска.
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(**filter_by)
                .options(
                    joinedload(DocumentField.template_field).joinedload(
                        TemplateField.type
                    )
                )
            )
            result: Result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, **filter_by) -> Sequence[DocumentField]:
        """Получить все объекты по заданному фильтру.

        Args:
            filter_by (dict): параметры для поиска объектов.

        Returns:
            list(Model): список объектов, удовлетворяющих фильтру поиска.
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(**filter_by)
                .options(
                    joinedload(DocumentField.template_field).joinedload(
                        TemplateField.type
                    )
                )
            )
            result: Result = await session.execute(query)
            return result.scalars().all()


class DocumentDAO(BaseDAO):
    model = Document

    @classmethod
    async def get_by_id(cls, model_id: int) -> Optional[Document]:
        """Получить документ с заданным идентификатором.

        Args:
            id (pk_type): идентификатор запрашиваемого документа.

        Returns:
            Document | None: документ с заданным id.
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id=model_id)
                .options(joinedload(Document.template))
                .options(
                    selectinload(Document.fields)
                    .joinedload(DocumentField.template_field)
                    .joinedload(TemplateField.type)
                )
            )
            result: Result = await session.execute(query)
            return result.unique().scalar_one_or_none()
