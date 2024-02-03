import os.path
from typing import Any

import pytest
from fastapi import UploadFile

from app.common.exceptions import (
    TemplateAlreadyDeletedException,
    TemplateNotFoundException,
    TypeFieldNotFoundException,
)
from app.config import settings
from app.crud.template_dao import TemplateDAO
from app.schemas.template import TemplateReadDTO, TemplateWriteDTO
from app.services.template import TemplateService
from app.tests.fixtures import (
    broken_docx_error_tags,
    broken_docx_path,
    template_with_invalid_type_field,
    templates_for_read,
    templates_for_write,
)


class TestTemplateService:
    def _compare_fields(self, field1, field2):
        assert field1.tag == field2.tag, "tag полей не совпадают"
        assert field1.name == field2.name, "name полей не совпадают"
        assert field1.hint == field2.hint, "hint полей не совпадают"
        assert field1.type == field2.type, "type полей не совпадают"
        assert field1.length == field2.length, "length полей не совпадают"
        assert field1.mask == field2.mask, "mask полей не совпадают"

    def _compare_groups(self, group1, group2):
        assert group1.name == group2.name, "Имена групп не совпадают"
        assert len(group1.fields) == len(
            group2.fields
        ), "Размеры групп не совпадают"
        for field1, field2 in zip(group1.fields, group2.fields):
            self._compare_fields(field1, field2)

    def _compare_templates(self, tpl1, tpl2):
        assert tpl1.title == tpl2.title
        assert tpl1.description == tpl2.description
        assert tpl1.deleted == tpl2.deleted
        assert tpl1.thumbnail == tpl2.thumbnail
        assert len(tpl1.grouped_fields) == len(tpl2.grouped_fields)
        assert len(tpl1.ungrouped_fields) == len(tpl2.ungrouped_fields)
        for group1, group2 in zip(tpl1.grouped_fields, tpl2.grouped_fields):
            self._compare_groups(group1, group2)
        for field1, field2 in zip(
            tpl1.ungrouped_fields, tpl2.ungrouped_fields
        ):
            self._compare_fields(field1, field2)

    async def _check_template_by_id(self, id, expected_dto: TemplateReadDTO):
        read_dto = await TemplateService.get(id=id)
        assert read_dto, "Объект не найден в базе"
        self._compare_templates(read_dto, expected_dto)

    async def test_get_invalid_id_raises_exception(self):
        with pytest.raises(TemplateNotFoundException):
            await TemplateService.get(id=100)

    @pytest.mark.parametrize(
        "write_data, read_data", zip(templates_for_write, templates_for_read)
    )
    async def test_add_and_delete(
        self,
        write_data: dict[str, Any],
        read_data: dict[str, Any],
    ):
        write_dto = TemplateWriteDTO(**write_data)
        db_len = len(await TemplateService.get_all())
        new_obj_id = await TemplateService.add(write_dto)
        assert new_obj_id, "Функция не вернула id нового объекта"
        new_db_len = len(await TemplateService.get_all())
        assert db_len + 1 == new_db_len, "Объект не добавлен в базу"

        # Чтение записи по id из базы
        expected_dto = TemplateReadDTO(**read_data)
        await self._check_template_by_id(new_obj_id, expected_dto)

        # удаление созданной записи
        await TemplateService.delete(new_obj_id)
        new_db_len = len(await TemplateService.get_all())
        assert new_db_len == db_len
        with pytest.raises(TemplateNotFoundException):
            obj_db = await TemplateService.get(id=new_obj_id)
            assert not obj_db, "Объект не удален из базы"

        with pytest.raises(TemplateAlreadyDeletedException):
            await TemplateService.delete(id=new_obj_id)
            assert (
                False
            ), "Удаление должно взводить TemplateAlreadyDeletedException"

    async def test_get_all_and_delete(self):
        db_len = len(await TemplateService.get_all())
        db_with_deleted_len = len(
            await TemplateService.get_all(include_deleted=True)
        )
        # добавление нескольких объектов в базу
        new_obj_ids = []
        for write_data in templates_for_write:
            write_dto = TemplateWriteDTO(**write_data)
            new_id = await TemplateService.add(write_dto)
            assert new_id, "Функция не вернула id нового объекта"
            new_obj_ids.append(new_id)
        new_db_len = len(await TemplateService.get_all())
        assert (
            db_len + len(templates_for_read) == new_db_len
        ), "Объекты не добавлены в базу"

        # проверка их наличия в базе
        expected_dtos = [TemplateReadDTO(**x) for x in templates_for_read]
        for id, expected_dto in zip(new_obj_ids, expected_dtos):
            await self._check_template_by_id(id, expected_dto)

        # удаление созданных записей
        for id in new_obj_ids:
            await TemplateService.delete(id)
            with pytest.raises(TemplateNotFoundException):
                obj_db = await TemplateService.get(id=id)
                assert not obj_db, "Объект не удален из базы"
        # проверка количества записей в б.д.
        new_db_len = len(await TemplateService.get_all())
        new_db_with_deleted_len = len(
            await TemplateService.get_all(include_deleted=True)
        )
        assert (
            db_len == new_db_len
        ), "Кол-во записей в б.д. не соответствует ожидаемым"
        assert new_db_with_deleted_len == db_with_deleted_len + len(
            new_obj_ids
        )

    async def test_post_invalid_type_raises_exception(self):
        new_obj = TemplateWriteDTO(**template_with_invalid_type_field)
        with pytest.raises(TypeFieldNotFoundException):
            new_id = await TemplateService.add(new_obj)
            assert new_id, "Создан объект с ошибочным типом"

    async def test_delete_invalid_id_raises_exception(self):
        with pytest.raises(TemplateNotFoundException):
            await TemplateService.delete(id=100)

    @pytest.mark.parametrize(
        "docx_path, broken_tags", [(broken_docx_path, broken_docx_error_tags)]
    )
    async def test_update_docx_template(self, docx_path, broken_tags):
        write_data = templates_for_write[0]
        write_dto = TemplateWriteDTO(**write_data)
        tpl_id = await TemplateService.add(write_dto)
        assert tpl_id, "Функция не вернула id нового объекта"
        with open(docx_path, "rb") as test_file:
            upload_file = UploadFile(
                file=test_file, filename="broken_template1.docx"
            )
            await TemplateService.update_docx_template(
                tpl_id, file=upload_file
            )
        expected_name = f"tpl_{tpl_id}.docx"
        expected_path = settings.TEMPLATE_DOCX_DIR + expected_name
        print(expected_name)
        tpl = await TemplateDAO.get_by_id(tpl_id)
        assert tpl.filename, "Шаблон не загружен"
        assert tpl.filename.name == expected_name, "Ошибочное имя docx"
        assert os.path.samefile(
            tpl.filename.path, expected_path
        ), "Ошибочный путь docx"

        # проверка get_inconsistent_tags
        inconsistent_tags = await TemplateService.get_inconsistent_tags(tpl_id)
        assert inconsistent_tags == broken_tags, "Ошибка проверки тэгов"
        # assert os.path.exists("")

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
