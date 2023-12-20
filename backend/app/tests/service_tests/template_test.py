import pytest
from app.common.exceptions import TemplateNotFoundException
from app.schemas.template import TemplateWriteDTO
from app.services.template import TemplateService
from app.services.template_field_type import TemplateFieldTypeService

templates_for_write = [
    {
        "title": "Шаблон 1",
        "deleted": "False",
        "description": "Описание шаблона 1",
        "grouped_fields": [
            {
                "name": "Группа 1",
                "fields": [
                    {
                        "tag": "Тэг1",
                        "name": "Наименование 1",
                        "hint": "Описание 1",
                        "type": "str",
                        "length": 100,
                    },
                    {
                        "tag": "Тэг2",
                        "name": "Наименование 2",
                        "hint": "Описание 2",
                        "type": "int",
                        "length": 20,
                    },
                ],
            },
            {
                "name": "Группа 2",
                "fields": [
                    {
                        "tag": "Тэг3",
                        "name": "Наименование 3",
                        "hint": "Описание 3",
                        "type": "str",
                        "length": 40,
                    },
                    {
                        "tag": "Тэг4",
                        "name": "Наименование 4",
                        "hint": "Описание 4",
                        "type": "float",
                        "length": 40,
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "tag": "Тэг5",
                "name": "Наименование 5",
                "hint": "Описание 5",
                "type": "str",
                "length": 100,
            },
            {
                "tag": "Тэг6",
                "name": "Наименование 6",
                "hint": "Описание 6",
                "type": "str",
                "length": 100,
            },
        ],
    },
    {
        "title": "Шаблон 2",
        "deleted": "False",
        "description": "Описание шаблона 2",
        "grouped_fields": [
            {
                "name": "Группа 3",
                "fields": [
                    {
                        "tag": "Тэг 7",
                        "name": "Наименование 7",
                        "hint": "Описание 7",
                        "type": "str",
                        "length": 100,
                    },
                    {
                        "tag": "Тэг8",
                        "name": "Наименование 8",
                        "hint": "Описание 8",
                        "type": "int",
                        "length": 20,
                    },
                ],
            },
            {
                "name": "Группа 4",
                "fields": [
                    {
                        "tag": "Тэг9",
                        "name": "Наименование 9",
                        "hint": "Описание 9",
                        "type": "str",
                        "length": 40,
                    },
                    {
                        "tag": "Тэг10",
                        "name": "Наименование 10",
                        "hint": "Описание 10",
                        "type": "float",
                        "length": 40,
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "tag": "Тэг11",
                "name": "Наименование 11",
                "hint": "Описание 11",
                "type": "str",
                "length": 100,
            },
            {
                "tag": "Тэг12",
                "name": "Наименование 12",
                "hint": "Описание 12",
                "type": "str",
                "length": 100,
            },
        ],
    },
]

templates_for_read = [
    {
        "title": "Шаблон 1",
        "deleted": "False",
        "description": "Описание шаблона 1",
        "grouped_fields": [
            {
                "name": "Группа 1",
                "fields": [
                    {
                        "tag": "Тэг1",
                        "name": "Наименование 1",
                        "hint": "Описание 1",
                        "type": "str",
                        "length": 100,
                    },
                    {
                        "tag": "Тэг2",
                        "name": "Наименование 2",
                        "hint": "Описание 2",
                        "type": "int",
                        "length": 20,
                    },
                ],
            },
            {
                "name": "Группа 2",
                "fields": [
                    {
                        "tag": "Тэг3",
                        "name": "Наименование 3",
                        "hint": "Описание 3",
                        "type": "str",
                        "length": 40,
                    },
                    {
                        "tag": "Тэг4",
                        "name": "Наименование 4",
                        "hint": "Описание 4",
                        "type": "float",
                        "length": 40,
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "tag": "Тэг5",
                "name": "Наименование 5",
                "hint": "Описание 5",
                "type": "str",
                "length": 100,
            },
            {
                "tag": "Тэг6",
                "name": "Наименование 6",
                "hint": "Описание 6",
                "type": "str",
                "length": 100,
            },
        ],
    },
    {
        "title": "Шаблон 2",
        "deleted": "False",
        "description": "Описание шаблона 2",
        "grouped_fields": [
            {
                "name": "Группа 3",
                "fields": [
                    {
                        "tag": "Тэг 7",
                        "name": "Наименование 7",
                        "hint": "Описание 7",
                        "type": "str",
                        "length": 100,
                    },
                    {
                        "tag": "Тэг8",
                        "name": "Наименование 8",
                        "hint": "Описание 8",
                        "type": "int",
                        "length": 20,
                    },
                ],
            },
            {
                "name": "Группа 4",
                "fields": [
                    {
                        "tag": "Тэг9",
                        "name": "Наименование 9",
                        "hint": "Описание 9",
                        "type": "str",
                        "length": 40,
                    },
                    {
                        "tag": "Тэг10",
                        "name": "Наименование 10",
                        "hint": "Описание 10",
                        "type": "float",
                        "length": 40,
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "tag": "Тэг11",
                "name": "Наименование 11",
                "hint": "Описание 11",
                "type": "str",
                "length": 100,
            },
            {
                "tag": "Тэг12",
                "name": "Наименование 12",
                "hint": "Описание 12",
                "type": "str",
                "length": 100,
            },
        ],
    },
]

# # Построение словаря исходных данных с ключом id
# template_field_type_dict = {x[0]: x[1:] for x in template_field_type_mock[1]}

# # Построение словаря соответвий type:id
# template_field_type_id_mapping = {
#     x[1]: x[0] for x in template_field_type_mock[1]
# }


class TestTemplateService:
    # @pytest.mark.parametrize(*template_field_type_mock)
    # async def test_get_success(self, id, type, name, mask):
    #     obj_dto = await TemplateFieldTypeService.get(id=id)
    #     assert obj_dto
    #     assert isinstance(obj_dto, TemplateFieldTypeReadDTO)
    #     assert obj_dto.id == id
    #     assert obj_dto.type == type
    #     assert obj_dto.name == name
    #     assert obj_dto.mask == mask

    def _compare_templates(self, tpl1, tpl2):
        # assert isinstance(tpl1, (Template)
        assert tpl1.title == tpl2.title
        assert tpl1.description == tpl2.description
        assert tpl1.deleted == tpl2.deleted
        assert len(tpl1.grouped_fields) == len(tpl2.grouped_fields)
        assert len(tpl1.ungrouped_fields) == len(tpl2.ungrouped_fields)

    async def test_get_invalid_id_raises_exception(self):
        with pytest.raises(TemplateNotFoundException):
            obj_dto = await TemplateService.get(id=100)

    @pytest.mark.parametrize("data", templates_for_write)
    async def test_add_and_delete(self, data):
        write_dto = TemplateWriteDTO(**data)
        db_len = len(await TemplateService.get_all())
        new_obj_id = await TemplateService.add(write_dto)
        assert new_obj_id, "Функция не вернула id нового объекта"
        new_db_len = len(await TemplateService.get_all())
        assert db_len + 1 == new_db_len, "Объект не добавлен в базу"

        # Чтение записи по id из базы
        read_dto = await TemplateService.get(id=new_obj_id)
        assert read_dto, "Объект не найден в базе"
        self._compare_templates(write_dto, read_dto)
        # assert obj_db.id == new_dto.id
        # assert obj_db.type == new_dto.type
        # assert obj_db.name == new_dto.name
        # assert obj_db.mask == new_dto.mask

        # удаление созданной записи
        # await TemplateService.delete(id)
        # new_db_len = len(await TemplateService.get_all())
        # assert new_db_len == db_len
        # with pytest.raises(TemplateNotFoundException):
        #     obj_db = await TemplateService.get(id=id)
        #     assert not obj_db, "Объект не удален из базы"
        # new_db_len = len(await TemplateService.get_all(include_deleted=True))
        # assert (
        #     new_db_len == db_len + 1
        # ), "Объект удален, а не помечен как удаленный"

    # async def test_get_all(self):
    #     dto_list = await TemplateFieldTypeService.get_all()
    #     assert len(dto_list) == len(template_field_type_dict)
    #     unique_id_db = set(dto_list.id for dto_list in dto_list)
    #     assert len(unique_id_db) == len(
    #         template_field_type_dict
    #     ), "Ответ содержит дублирующиеся id"
    #     for dto in dto_list:
    #         dto_fields = (dto.type, dto.name, dto.mask)
    #         assert (
    #             template_field_type_dict[dto.id] == dto_fields
    #         ), "Поля ответа не соответствуют ожидаемым"

    # @pytest.mark.parametrize(*template_field_type_mock)
    # async def test_add_duplicate_type_raises_exception(
    #     self, id, type, name, mask
    # ):
    #     new_obj = TemplateFieldTypeWriteDTO(type=type, name="", mask="")
    #     with pytest.raises(TypeFieldAlreadyExistsException):
    #         await TemplateFieldTypeService.add(new_obj)

    # async def test_delete_invalid_id_raises_exception(self):
    #     with pytest.raises(TypeFieldNotFoundException):
    #         await TemplateFieldTypeService.delete(id=100)

    # async def test_update(self):
    #     new_obj = TemplateFieldTypeWriteDTO(
    #         type="currency", name="Валюта", mask="маска"
    #     )
    #     updated_obj = TemplateFieldTypeWriteDTO(
    #         type="updated_currency",
    #         name="Валюта изм.",
    #         mask="новая маска",
    #     )
    #     obj_dto = await TemplateFieldTypeService.add(new_obj)
    #     assert obj_dto, "Объект не добавлен в базу"
    #     id = obj_dto.id
    #     obj_dto = await TemplateFieldTypeService.update(id, updated_obj)
    #     assert obj_dto, "Сервис не вернул обновленный объект"
    #     assert obj_dto.type == updated_obj.type
    #     assert obj_dto.name == updated_obj.name
    #     assert obj_dto.mask == updated_obj.mask

    #     # Чтение записи по id из базы
    #     id = obj_dto.id
    #     obj_dto = await TemplateFieldTypeService.get(id=id)
    #     assert obj_dto.type == updated_obj.type
    #     assert obj_dto.name == updated_obj.name
    #     assert obj_dto.mask == updated_obj.mask

    #     # удаление созданной записи
    #     await TemplateFieldTypeService.delete(id)

    #     # обновление несуществующего объекта
    #     with pytest.raises(TypeFieldNotFoundException):
    #         obj_dto = await TemplateFieldTypeService.update(100, updated_obj)
    #         assert (
    #             not obj_dto
    #         ), "Обновление несуществующего id не вызвало исключение"

    #     # обновление дубликатным типом
    #     with pytest.raises(TypeFieldAlreadyExistsException):
    #         updated_obj.type = "str"
    #         obj_dto = await TemplateFieldTypeService.update(3, updated_obj)
    #         assert (
    #             not obj_dto
    #         ), "Добавление типа дубликата не вызвало исключение"

    # @pytest.mark.parametrize(*template_field_type_mock)
    # async def test_get_all_type_id_mapping(self, id, type, name, mask):
    #     type_id_mapping = (
    #         await TemplateFieldTypeService.get_all_type_id_mapping()
    #     )
    #     assert type_id_mapping == template_field_type_id_mapping
