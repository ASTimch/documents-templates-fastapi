from datetime import date
from typing import Optional

from sqlalchemy import Result, Sequence, and_, func, or_, select, update
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base_dao import BaseDAO
from app.database import async_session_maker
from app.models.document import Document, DocumentField
from app.models.favorite import UserTemplateFavorite

# from app.hotels.schemas import SHotelRead
from app.models.template import Template, TemplateField, TemplateFieldType


class DocumentFieldDAO(BaseDAO):
    model = DocumentField

    @classmethod
    async def get_by_id(cls, model_id: int) -> Optional[DocumentField]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id=model_id)
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
                # .options(selectinload(Document.favorited_by_users))
            )
            result: Result = await session.execute(query)
            return result.unique().scalar_one_or_none()
