import pytest
from app.crud.template_dao import TemplateFieldTypeDAO


# {
#     "id": 1,
#     "type": "str",
#     "name": "Строка",
#     "mask": "/^.*$/"
# },
# {
#     "id": 2,
#     "type": "int",
#     "name": "Целочисленный",
#     "mask": "/^\\d*$/"
# },
# {
#     "id": 3,
#     "type": "float",
#     "name": "Вещественный",
#     "mask": "/^\\d+(?:\\.|,)?\\d*$/"
# }

field_type_db = {
    1: ("str", "Строка", "/^.*$/"),
    2: ("int", "Целочисленный", "/^\\d*$/"),
    3: ("float", "Вещественный", "/^\\d+(?:\\.|,)?\\d*$/"),
}

template_field_type_mock = (
    "id, type, name, mask, exists",
    [
        (1, "str", "Строка", "/^.*$/", True),
        (2, "int", "Целочисленный", "/^\\d*$/", True),
        (3, "float", "Вещественный", "/^\\d+(?:\\.|,)?\\d*$/", True),
        (100, "unknown", "Несуществующий тип", "", False),
    ],
)


@pytest.mark.parametrize(*template_field_type_mock)
async def test_field_type_dao_get_by_id(id, type, name, mask, exists):
    obj_db = await TemplateFieldTypeDAO.get_by_id(id)
    if exists:
        assert obj_db
        assert id == obj_db.id
        assert name == obj_db.name
        assert type == obj_db.type
        assert mask == obj_db.mask
    else:
        assert not obj_db


@pytest.mark.parametrize(*template_field_type_mock)
async def test_field_type_dao_get_one_or_none(id, type, name, mask, exists):
    obj_db = await TemplateFieldTypeDAO.get_one_or_none(type=type)
    if exists:
        assert obj_db
        assert id == obj_db.id
        assert name == obj_db.name
        assert type == obj_db.type
        assert mask == obj_db.mask
    else:
        assert not obj_db


async def test_field_type_dao_get_all():
    obj_db_sequence = await TemplateFieldTypeDAO.get_all()
    assert len(obj_db_sequence) == len(field_type_db)
    unique_id_db = set(obj_db.id for obj_db in obj_db_sequence)
    assert len(unique_id_db) == len(
        field_type_db
    ), "Ответ содержит дублирующиеся id"
    for obj_db in obj_db_sequence:
        obj_db_fields = (obj_db.type, obj_db.name, obj_db.mask)
        assert (
            field_type_db[obj_db.id] == obj_db_fields
        ), "Поля ответа не соответствуют ожидаемым"


async def test_field_type_dao_create_delete():
    new_obj = {"type": "currency", "name": "Валюта", "mask": "маска"}

    db_len = len(await TemplateFieldTypeDAO.get_all())
    obj_db = await TemplateFieldTypeDAO.create(**new_obj)
    assert obj_db, "Функция не вернула созданный объект"
    assert obj_db.type == new_obj["type"]
    assert obj_db.name == new_obj["name"]
    assert obj_db.mask == new_obj["mask"]
    new_db_len = len(await TemplateFieldTypeDAO.get_all())
    assert db_len + 1 == new_db_len, "Объект не добавлен в базу"

    # Чтение записи по id из базы
    id = obj_db.id
    obj_db = await TemplateFieldTypeDAO.get_by_id(id)
    assert obj_db, "Объект не добавлен в базу"
    assert obj_db.type == new_obj["type"]
    assert obj_db.name == new_obj["name"]
    assert obj_db.mask == new_obj["mask"]

    # удаление созданной записи
    await TemplateFieldTypeDAO.delete_(id)
    new_db_len = len(await TemplateFieldTypeDAO.get_all())
    assert new_db_len == db_len
    obj_db = await TemplateFieldTypeDAO.get_by_id(id)
    assert not obj_db, "Объект не удален из базы"


async def test_field_type_dao_update():
    new_obj = {"type": "currency", "name": "Валюта", "mask": "маска"}
    updated_obj = {
        "type": "updateed_currency",
        "name": "Валюта изм.",
        "mask": "новая маска",
    }
    obj_db = await TemplateFieldTypeDAO.create(**new_obj)
    assert obj_db
    id = obj_db.id
    obj_db = await TemplateFieldTypeDAO.update_(id, **updated_obj)

    # Чтение записи по id из базы
    id = obj_db.id
    obj_db = await TemplateFieldTypeDAO.get_by_id(id)
    assert obj_db, "Объект не добавлен в базу"
    assert obj_db.type == updated_obj["type"]
    assert obj_db.name == updated_obj["name"]
    assert obj_db.mask == updated_obj["mask"]

    # удаление созданной записи
    await TemplateFieldTypeDAO.delete_(id)
