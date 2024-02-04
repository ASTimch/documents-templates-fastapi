from typing import Optional

from sqlalchemy import Result, select
from sqlalchemy.orm import selectinload

from app.crud.base_dao import BaseDAO
from app.database import async_session_maker
from app.models.base import pk_type
from app.models.favorite import UserTemplateFavorite
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
    async def get_by_id(cls, id: pk_type) -> Optional[Template]:
        """Получить шаблон с заданным идентификатором.

        Args:
            id (pk_type): идентификатор запрашиваемого шаблона.

        Returns:
            Template | None: шаблон с заданным id.
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id=id)
                .options(selectinload(Template.groups))
                .options(
                    selectinload(Template.fields).joinedload(
                        TemplateField.type
                    )
                )
                .options(selectinload(Template.favorited_by_users))
            )
            result: Result = await session.execute(query)
            return result.unique().scalar_one_or_none()

    @classmethod
    async def delete_(cls, id: pk_type) -> None:
        raise NotImplementedError
        # async with async_session_maker() as session:
        #     stmt = (
        #         update(cls.model)
        #         .where(cls.model.id == id)
        #         .values(deleted=True)
        #     )
        #     await session.execute(stmt)
        #     await session.commit()


class UserTemplateFavoriteDAO(BaseDAO):
    model = UserTemplateFavorite
