from typing import Any, Optional
from httpx import AsyncClient
import pytest
from app.config import settings
from app.schemas.template import TemplateWriteDTO
from app.services.template import TemplateService
from app.tests.fixtures import templates_for_write, templates_for_read


@pytest.mark.parametrize("route", [settings.API_V1_PREFIX + "/template/"])
class TestTemplateApiV1:
    def _compare_dicts(self, dct1, dct2, skip_keys: Optional[set[str]] = None):
        if skip_keys is None:
            skip_keys = set()
        keys1 = list(sorted(dct1.keys()))
        keys2 = list(sorted(dct2.keys()))
        for key1, key2 in zip(keys1, keys2):
            assert key1 == key2
            if key1 in skip_keys:
                continue
            if isinstance(dct1[key1], list):
                for v1, v2 in zip(dct1[key1], dct2[key2]):
                    self._compare_dicts(v1, v2, skip_keys)
            else:
                assert dct1[key1] == dct2[key2]

    @pytest.mark.parametrize("write_data", [templates_for_write[0]])
    async def test_post_delete_for_anauthorized(
        self, route, ac: AsyncClient, write_data
    ):
        # добавление шаблона
        response = await ac.post(route, json=write_data)
        assert response.status_code == 401

        # удаление шаблона
        response = await ac.delete(route + "1")
        assert response.status_code == 401

        # добавление в избранное
        response = await ac.post(route + "1/favorite/")
        assert response.status_code == 401

        # удаление из избранного
        response = await ac.delete(route + "1/favorite/")
        assert response.status_code == 401

    @pytest.mark.parametrize("write_data", [templates_for_write[0]])
    async def test_post_delete_for_regular_user(
        self, route, user_ac: AsyncClient, write_data
    ):
        # добавление шаблона
        response = await user_ac.post(route, json=write_data)
        assert response.status_code == 403

        # удаление шаблона
        response = await user_ac.delete(route + "1")
        assert response.status_code == 403

    @pytest.mark.parametrize("write_data", [templates_for_write[0]])
    async def test_favorite_for_regular_user(
        self, route, user_ac: AsyncClient, write_data
    ):
        template_dto = TemplateWriteDTO.model_validate(write_data)
        template_id = await TemplateService.add(template_dto)

        # добавление в избранное
        response = await user_ac.post(route + f"{template_id}/favorite/")
        assert response.status_code == 201

        # повторное добавление в избранное
        response = await user_ac.post(route + f"{template_id}/favorite/")
        assert response.status_code == 409

        # удаление из избранного
        response = await user_ac.delete(route + f"{template_id}/favorite/")
        assert response.status_code == 204

        # повторное удаление из избранного
        response = await user_ac.delete(route + f"{template_id}/favorite/")
        assert response.status_code == 404

        # удаление из избранного отсутствующего шаблона
        response = await user_ac.delete(route + f"{template_id}/favorite/")
        assert response.status_code == 404

        await TemplateService.delete(template_id)

    @pytest.mark.parametrize(
        "write_data, read_data", zip(templates_for_write, templates_for_read)
    )
    async def test_post_delete(
        self,
        route,
        superuser_ac: AsyncClient,
        write_data: dict[str, Any],
        read_data: dict[str, Any],
    ):
        response = await superuser_ac.post(route, json=write_data)
        assert response.status_code == 201
        response_dict = response.json()
        self._compare_dicts(
            response_dict,
            read_data,
            set(["created_at", "updated_at", "id"]),
        )
        new_obj_id = response_dict.get("id")

        # чтение вновь созданной записи
        response = await superuser_ac.get(route + str(new_obj_id))
        assert response.status_code == 200
        response_dict = response.json()
        self._compare_dicts(
            response_dict,
            read_data,
            set(["created_at", "updated_at", "id"]),
        )

        # удаление записи
        response = await superuser_ac.delete(route + str(new_obj_id))
        assert response.status_code == 204
        # проверка, что теперь 410 для удаленного шаблона
        response = await superuser_ac.delete(route + str(new_obj_id))
        assert response.status_code == 410

        # проверка, что теперь 404 для удаленного шаблона
        response = await superuser_ac.get(route + str(new_obj_id))
        assert response.status_code == 404

        # проверка 404 для отсутствующего шаблона
        response = await superuser_ac.get(route + str(999))
        assert response.status_code == 404

    async def test_get(self, route, superuser_ac: AsyncClient):
        # добавление двух шаблонов
        response_dicts = []
        for write_data in templates_for_write:
            response = await superuser_ac.post(route, json=write_data)
            assert response.status_code == 201
            response_dicts.append(response.json())

        response = await superuser_ac.get(route)
        assert response.status_code == 200
        response_list = response.json()
        print(response_list)
        assert len(response_list) == len(response_dicts)
        for full_dict, minified_dict in zip(response_dicts, response_list):
            full_dict.pop("grouped_fields")
            full_dict.pop("ungrouped_fields")
            self._compare_dicts(full_dict, minified_dict)

        # удаление созданных записей
        for response in response_dicts:
            response = await superuser_ac.delete(route + str(response["id"]))
            assert response.status_code == 204

        # проверка, что все удалено
        response = await superuser_ac.get(route)
        assert response.status_code == 200
        response_list = response.json()
        assert len(response_list) == 0
