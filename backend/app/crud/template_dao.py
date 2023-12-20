from datetime import date
from typing import Optional

from sqlalchemy import Result, and_, func, or_, select, update
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base_dao import BaseDAO
from app.database import async_session_maker

# from app.hotels.schemas import SHotelRead
from app.models.template import (
    Template,
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
)


class TemplateFieldTypeDAO(BaseDAO):
    model = TemplateFieldType


class TemplateFieldGroupDAO(BaseDAO):
    model = TemplateFieldType


class TemplateFieldGroupDAO(BaseDAO):
    model = TemplateFieldGroup


class TemplateFieldDAO(BaseDAO):
    model = TemplateField


class TemplateDAO(BaseDAO):
    model = Template

    @classmethod
    async def get_by_id(cls, model_id: int) -> Optional[Template]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id=model_id)
                .options(selectinload(Template.groups))
                .options(
                    selectinload(Template.fields).joinedload(
                        TemplateField.type
                    )
                )
            )
            result: Result = await session.execute(query)
            return result.unique().scalar_one_or_none()

    @classmethod
    async def delete_(cls, id: int) -> None:
        raise NotImplementedError
        # async with async_session_maker() as session:
        #     stmt = (
        #         update(cls.model)
        #         .where(cls.model.id == id)
        #         .values(deleted=True)
        #     )
        #     await session.execute(stmt)
        #     await session.commit()
