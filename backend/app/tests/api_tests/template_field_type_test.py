import pytest
from httpx import AsyncClient

from app.config import settings

expected_get_json = [
    {"id": 1, "type": "str", "name": "Строка", "mask": "/^.*$/"},
    {"id": 2, "type": "int", "name": "Целочисленный", "mask": "/^\\d*$/"},
    {
        "id": 3,
        "type": "float",
        "name": "Вещественный",
        "mask": "/^\\d+(?:\\.|,)?\\d*$/",
    },
]

new_type_json = {"type": "currency", "name": "валюта", "mask": "^\\d+$"}
duplicate_type_json = {"type": "int", "name": "валюта", "mask": "^\\d+$"}


@pytest.mark.parametrize(
    "route", [settings.API_V1_PREFIX + "/template_field_type/"]
)
class TestFieldTypeApiV1:
    async def test_get(self, route, ac: AsyncClient):
        response = await ac.get(route)
        assert response.status_code == 200
        types_list = response.json()
        assert len(types_list) == 3
        assert types_list == expected_get_json

    @pytest.mark.parametrize("id", [1, 2, 3])
    async def test_get_by_id(self, route, id, ac: AsyncClient):
        response = await ac.get(route + str(id))
        assert response.status_code == 200
        type_dict = response.json()
        assert type_dict == expected_get_json[id - 1]

    async def test_post_patch_delete(self, route, ac: AsyncClient):
        response = await ac.post(route, json=new_type_json)
        assert response.status_code == 201
        type_dict = response.json()
        id = type_dict.pop("id")
        assert type_dict == new_type_json

        # чтение вновь созданной записи
        response = await ac.get(route + str(id))
        assert response.status_code == 200
        type_dict = response.json()
        id = type_dict.pop("id")
        assert type_dict == new_type_json

        # обновление добавленной записи
        updated_type_json = {
            "type": "new_currency",
            "name": "new_валюта",
            "mask": "111",
        }
        response = await ac.put(route + str(id), json=updated_type_json)
        assert response.status_code == 200
        type_dict = response.json()
        id = type_dict.pop("id")
        assert type_dict == updated_type_json

        # удаление обновленной записи
        response = await ac.delete(route + str(id))
        assert response.status_code == 204

        response = await ac.get(route + str(id))
        assert response.status_code == 404

    async def test_post_update_duplicate_types(self, route, ac: AsyncClient):
        response = await ac.post(route, json=duplicate_type_json)
        assert response.status_code == 409
        assert response.json().get("detail") == "Тип поля int уже существует"
        response = await ac.put(route + "1", json=duplicate_type_json)
        assert response.status_code == 409
        assert response.json().get("detail") == "Тип поля int уже существует"
