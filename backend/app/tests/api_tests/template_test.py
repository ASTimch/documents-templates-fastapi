import json
from typing import Any, Optional
from httpx import AsyncClient
import pytest
from app.config import settings
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

    @pytest.mark.parametrize(
        "write_data, read_data", zip(templates_for_write, templates_for_read)
    )
    async def test_post_delete(
        self,
        route,
        ac: AsyncClient,
        write_data: dict[str, Any],
        read_data: dict[str, Any],
    ):
        response = await ac.post(route, json=write_data)
        assert response.status_code == 201
        response_dict = response.json()
        self._compare_dicts(
            response_dict,
            read_data,
            set(["created_at", "updated_at", "id"]),
        )
        new_obj_id = response_dict.get("id")

        # чтение вновь созданной записи
        response = await ac.get(route + str(new_obj_id))
        assert response.status_code == 200
        response_dict = response.json()
        self._compare_dicts(
            response_dict,
            read_data,
            set(["created_at", "updated_at", "id"]),
        )

        # удаление записи
        response = await ac.delete(route + str(new_obj_id))
        assert response.status_code == 204
        # проверка, что теперь 410 для удаленного шаблона
        response = await ac.delete(route + str(new_obj_id))
        assert response.status_code == 410

        # проверка, что теперь 404 для удаленного шаблона
        response = await ac.get(route + str(new_obj_id))
        assert response.status_code == 404

        # проверка 404 для отсутствующего шаблона
        response = await ac.get(route + str(999))
        assert response.status_code == 404

    async def test_get(self, route, ac: AsyncClient):
        # добавление двух шаблонов
        response_dicts = []
        for write_data in templates_for_write:
            response = await ac.post(route, json=write_data)
            assert response.status_code == 201
            response_dicts.append(response.json())

        response = await ac.get(route)
        assert response.status_code == 200
        response_list = response.json()
        assert len(response_list) == len(response_dicts)
        for full_dict, minified_dict in zip(response_dicts, response_list):
            full_dict.pop("grouped_fields")
            full_dict.pop("ungrouped_fields")
            self._compare_dicts(full_dict, minified_dict)

        # удаление созданных записей
        for response in response_dicts:
            response = await ac.delete(route + str(response["id"]))
            assert response.status_code == 204

        # проверка, что все удалено
        response = await ac.get(route)
        assert response.status_code == 200
        response_list = response.json()
        assert len(response_list) == 0
