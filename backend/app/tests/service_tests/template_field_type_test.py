from typing import Any
import pytest
from app.common.exceptions import (
    TypeFieldAlreadyExistsException,
    TypeFieldNotFoundException,
)
from app.schemas.template import (
    TemplateFieldTypeReadDTO,
    TemplateFieldTypeWriteDTO,
)
from app.services.template_field_type import TemplateFieldTypeService

template_field_type_mock = (
    "id, type, name, mask",
    [
        (1, "str", "Строка", "/^.*$/"),
        (2, "int", "Целочисленный", "/^\\d*$/"),
        (3, "float", "Вещественный", "/^\\d+(?:\\.|,)?\\d*$/"),
    ],
)

# Построение словаря исходных данных с ключом id
template_field_type_dict = {x[0]: x[1:] for x in template_field_type_mock[1]}

# Построение словаря соответствий type:id
template_field_type_id_mapping = {
    x[1]: x[0] for x in template_field_type_mock[1]
}


class TestFieldTypeService:
    @pytest.mark.parametrize(*template_field_type_mock)
    async def test_get_success(self, id, type, name, mask):
        obj_dto = await TemplateFieldTypeService.get(id=id)
        assert obj_dto
        assert isinstance(obj_dto, TemplateFieldTypeReadDTO)
        assert obj_dto.id == id
        assert obj_dto.type == type
        assert obj_dto.name == name
        assert obj_dto.mask == mask

    async def test_get_invalid_id_raises_exception(self):
        with pytest.raises(TypeFieldNotFoundException):
            obj_dto = await TemplateFieldTypeService.get(id=100)

    async def test_get_all(self):
        dto_list = await TemplateFieldTypeService.get_all()
        assert len(dto_list) == len(template_field_type_dict)
        unique_id_db = set(dto_list.id for dto_list in dto_list)
        assert len(unique_id_db) == len(
            template_field_type_dict
        ), "Ответ содержит дублирующиеся id"
        for dto in dto_list:
            dto_fields = (dto.type, dto.name, dto.mask)
            assert (
                template_field_type_dict[dto.id] == dto_fields
            ), "Поля ответа не соответствуют ожидаемым"

    async def test_field_type_add_delete(self):
        new_obj = TemplateFieldTypeWriteDTO(
            type="currency", name="Валюта", mask="маска"
        )

        db_len = len(await TemplateFieldTypeService.get_all())
        new_dto = await TemplateFieldTypeService.add(new_obj)
        assert new_dto, "Функция не вернула созданный объект"
        assert new_dto.type == new_obj.type
        assert new_dto.name == new_obj.name
        assert new_dto.mask == new_obj.mask
        new_db_len = len(await TemplateFieldTypeService.get_all())
        assert db_len + 1 == new_db_len, "Объект не добавлен в базу"

        # Чтение записи по id из базы
        id = new_dto.id
        obj_db = await TemplateFieldTypeService.get(id=id)
        assert obj_db, "Объект не добавлен в базу"
        assert obj_db.id == new_dto.id
        assert obj_db.type == new_dto.type
        assert obj_db.name == new_dto.name
        assert obj_db.mask == new_dto.mask

        # удаление созданной записи
        await TemplateFieldTypeService.delete(id)
        new_db_len = len(await TemplateFieldTypeService.get_all())
        assert new_db_len == db_len
        with pytest.raises(TypeFieldNotFoundException):
            obj_db = await TemplateFieldTypeService.get(id=id)
            assert not obj_db, "Объект не удален из базы"

    @pytest.mark.parametrize(*template_field_type_mock)
    async def test_add_duplicate_type_raises_exception(
        self, id, type, name, mask
    ):
        new_obj = TemplateFieldTypeWriteDTO(type=type, name="", mask="")
        with pytest.raises(TypeFieldAlreadyExistsException):
            await TemplateFieldTypeService.add(new_obj)

    async def test_delete_invalid_id_raises_exception(self):
        with pytest.raises(TypeFieldNotFoundException):
            await TemplateFieldTypeService.delete(id=100)

    async def test_update(self):
        new_obj = TemplateFieldTypeWriteDTO(
            type="currency", name="Валюта", mask="маска"
        )
        updated_obj = TemplateFieldTypeWriteDTO(
            type="updated_currency",
            name="Валюта изм.",
            mask="новая маска",
        )
        obj_dto = await TemplateFieldTypeService.add(new_obj)
        assert obj_dto, "Объект не добавлен в базу"
        id = obj_dto.id
        obj_dto = await TemplateFieldTypeService.update(id, updated_obj)
        assert obj_dto, "Сервис не вернул обновленный объект"
        assert obj_dto.type == updated_obj.type
        assert obj_dto.name == updated_obj.name
        assert obj_dto.mask == updated_obj.mask

        # Чтение записи по id из базы
        id = obj_dto.id
        obj_dto = await TemplateFieldTypeService.get(id=id)
        assert obj_dto.type == updated_obj.type
        assert obj_dto.name == updated_obj.name
        assert obj_dto.mask == updated_obj.mask

        # удаление созданной записи
        await TemplateFieldTypeService.delete(id)

        # обновление несуществующего объекта
        with pytest.raises(TypeFieldNotFoundException):
            obj_dto = await TemplateFieldTypeService.update(100, updated_obj)
            assert (
                not obj_dto
            ), "Обновление несуществующего id не вызвало исключение"

        # обновление дубликатным типом
        with pytest.raises(TypeFieldAlreadyExistsException):
            updated_obj.type = "str"
            obj_dto = await TemplateFieldTypeService.update(3, updated_obj)
            assert (
                not obj_dto
            ), "Добавление типа дубликата не вызвало исключение"

    @pytest.mark.parametrize(*template_field_type_mock)
    async def test_get_all_type_id_mapping(self, id, type, name, mask):
        type_id_mapping = (
            await TemplateFieldTypeService.get_all_type_id_mapping()
        )
        assert type_id_mapping == template_field_type_id_mapping
