import pytest
from app.common.exceptions import (
    UserTemplateFavoriteAlreadyExistsException,
    UserTemplateFavoriteDoesNotExistsException,
)
from app.crud.template_dao import UserTemplateFavoriteDAO
from app.schemas.template import TemplateWriteDTO
from app.services.favorite import TemplateFavoriteService
from app.tests.fixtures import templates_for_write
from app.services.template import TemplateService


class TestTemplateFavoriteService:
    @pytest.mark.parametrize("user_id", [1, 2])
    async def test_add_delete_favorite(self, user_id):
        # добавление нескольких объектов в базу
        new_obj_ids = []
        for write_data in templates_for_write:
            write_dto = TemplateWriteDTO(**write_data)
            new_id = await TemplateService.add(write_dto)
            new_obj_ids.append(new_id)
        template_id = new_obj_ids[0]

        is_favorited = await TemplateFavoriteService.is_favorited(
            user_id, template_id
        )
        assert not is_favorited, "Неверное is_favorited"
        result = await TemplateFavoriteService.add_favorite(
            user_id, template_id
        )
        assert result.id
        connection_id = result.id
        #
        obj_in_db = await UserTemplateFavoriteDAO.get_by_id(connection_id)
        assert (
            obj_in_db.id == connection_id
        ), "Функция add_favorite вернула неверный объект"
        assert obj_in_db.user_id == user_id, "add_favorite: user_id неверен"
        assert (
            obj_in_db.template_id == template_id
        ), "add_favorite: template_id неверен"

        is_favorited = await TemplateFavoriteService.is_favorited(
            user_id, template_id
        )
        assert is_favorited == True, "Неверное is_favorited"

        # повторное добавление в избранное
        with pytest.raises(UserTemplateFavoriteAlreadyExistsException):
            result = await TemplateFavoriteService.add_favorite(
                user_id, template_id
            )
            assert result, "Повторное добавление шаблона в избранное"

        # удаление из избранного
        result = await TemplateFavoriteService.delete_favorite(
            user_id, template_id
        )
        #
        obj_in_db = await UserTemplateFavoriteDAO.get_by_id(connection_id)
        assert obj_in_db is None, "delete_favorite не удалила объект из базы"

        is_favorited = await TemplateFavoriteService.is_favorited(
            user_id, template_id
        )
        assert not is_favorited, "Неверное is_favorited"

        # удаление из избранного (если объекта нет в избранном)
        with pytest.raises(UserTemplateFavoriteDoesNotExistsException):
            result = await TemplateFavoriteService.delete_favorite(
                user_id, template_id
            )
            assert result, "Повторное удаление из избранного"

        # удаление созданных записей шаблонов
        for id in new_obj_ids:
            await TemplateService.delete(id)
