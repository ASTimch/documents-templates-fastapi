from app.common.exceptions import (
    UserTemplateFavoriteAlreadyExistsException,
    UserTemplateFavoriteDoesNotExistsException,
)

from app.crud.template_dao import UserTemplateFavoriteDAO


class TemplateFavoriteService:
    @classmethod
    async def add_favorite(cls, user_id: int, template_id: int):
        obj = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        print("obj=", obj)
        if obj:
            raise UserTemplateFavoriteAlreadyExistsException()
        return await UserTemplateFavoriteDAO.create(
            user_id=user_id, template_id=template_id
        )

    @classmethod
    async def delete_favorite(cls, user_id: int, template_id: int):
        obj = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        if not obj:
            raise UserTemplateFavoriteDoesNotExistsException()
        await UserTemplateFavoriteDAO.delete_(obj.id)
