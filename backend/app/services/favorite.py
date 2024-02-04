from app.common.exceptions import (
    UserTemplateFavoriteAlreadyExistsException,
    UserTemplateFavoriteDoesNotExistsException,
)
from app.crud.template_dao import UserTemplateFavoriteDAO


class TemplateFavoriteService:
    @classmethod
    async def add_favorite(cls, user_id: int, template_id: int):
        """Добавить шаблон в список избранного для пользователя.

        Args:
            user_id (int): идентификатор пользователя.
            template_id (int): идентификатор шаблона.

        Raises:
            UserTemplateFavoriteAlreadyExistsException: шаблон уже в избранном.
        """
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
        """Удалить шаблон из списка избранного для пользователя.

        Args:
            user_id (int): идентификатор пользователя.
            template_id (int): идентификатор шаблона.

        Raises:
            UserTemplateFavoriteDoesNotExistsException: шаблон не в избранном.
        """
        obj_db = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        if not obj_db:
            raise UserTemplateFavoriteDoesNotExistsException()
        await UserTemplateFavoriteDAO.delete_(obj_db.id)

    @classmethod
    async def is_favorited(cls, user_id: int, template_id: int) -> bool:
        """Находится ли шаблон в списке избранного для пользователя.

        Args:
            user_id (int): идентификатор пользователя.
            template_id (int): идентификатор шаблона.

        Return:
            bool: True, если шаблон содержится в списке избранного;
            False, если шаблон отсутствует в списке избранного.
        """
        obj_db = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        return obj_db is not None

    @classmethod
    async def get_user_favorite_ids(cls, user_id: int) -> list[int]:
        """Возвращает идентификаторы всех избранных шаблонов для пользователя.

        Args:
            user_id (int): идентификатор пользователя.

        Return:
            list[int]: список идентификаторов из списка избранного.
        """
        obj_db = await UserTemplateFavoriteDAO.get_all(user_id=user_id)
        return [obj.template_id for obj in obj_db]
