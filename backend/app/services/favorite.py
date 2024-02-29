from app.common.exceptions import (
    UserTemplateFavoriteAlreadyExistsException,
    UserTemplateFavoriteDoesNotExistsException,
)
from app.crud.template_dao import UserTemplateFavoriteDAO
from app.models.base import pk_type


class TemplateFavoriteService:
    @classmethod
    async def add_favorite(cls, user_id: pk_type, template_id: pk_type):
        """Добавить шаблон в список избранного для пользователя.

        Args:
            user_id: идентификатор пользователя.
            template_id: идентификатор шаблона.

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
    async def delete_favorite(cls, user_id: pk_type, template_id: pk_type):
        """Удалить шаблон из списка избранного для пользователя.

        Args:
            user_id: идентификатор пользователя.
            template_id: идентификатор шаблона.

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
    async def is_favorited(
        cls, user_id: pk_type, template_id: pk_type
    ) -> bool:
        """Находится ли шаблон в списке избранного для пользователя.

        Args:
            user_id: идентификатор пользователя.
            template_id: идентификатор шаблона.

        Returns:
            bool: True, если шаблон содержится в списке избранного;
            False, если шаблон отсутствует в списке избранного.
        """
        obj_db = await UserTemplateFavoriteDAO.get_one_or_none(
            user_id=user_id, template_id=template_id
        )
        return obj_db is not None

    @classmethod
    async def get_user_favorite_ids(cls, user_id: pk_type) -> list[pk_type]:
        """Возвращает идентификаторы всех избранных шаблонов для пользователя.

        Args:
            user_id: идентификатор пользователя.

        Returns:
            list[pk_type]: список идентификаторов из списка избранного.
        """
        obj_db = await UserTemplateFavoriteDAO.get_all(user_id=user_id)
        return [obj.template_id for obj in obj_db]
