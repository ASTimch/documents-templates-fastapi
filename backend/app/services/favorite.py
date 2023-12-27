from app.common.exceptions import (
    UserTemplateFavoriteAlreadyExistsException,
    UserTemplateFavoriteDoesNotExistsException,
)

from app.crud.template_dao import UserTemplateFavoriteDAO


class TemplateFavoriteService:
    @classmethod
    async def add_favorite(cls, user_id: int, template_id: int):
        obj_db = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        if obj_db:
            raise UserTemplateFavoriteAlreadyExistsException()
        return await UserTemplateFavoriteDAO.create(
            user_id=user_id, template_id=template_id
        )

    @classmethod
    async def delete_favorite(cls, user_id: int, template_id: int):
        obj_db = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        if not obj_db:
            raise UserTemplateFavoriteDoesNotExistsException()
        await UserTemplateFavoriteDAO.delete_(obj_db.id)

    @classmethod
    async def is_favorited(cls, user_id: int, template_id: int):
        obj_db = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        return obj_db is not None
