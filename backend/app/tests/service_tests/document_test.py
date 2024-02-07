import os.path
from typing import Any

import pytest
from fastapi import UploadFile

from app.common.exceptions import (
    DocumentNotFoundException,
    TemplateAlreadyDeletedException,
    TemplateNotFoundException,
    TypeFieldNotFoundException,
)
from app.config import settings
from app.crud.template_dao import TemplateDAO
from app.schemas.document import DocumentReadDTO
from app.schemas.template import TemplateReadDTO, TemplateWriteDTO
from app.services.document import DocumentService
from app.services.template import TemplateService
from app.tests.fixtures import (
    documents_for_read,
    documents_for_write,
    template_with_invalid_type_field,
    templates_for_read,
    templates_for_write,
)


class TestDocumentService:
    def _compare_fields(self, field1, field2):
        assert field1.tag == field2.tag, "tag полей не совпадают"
        assert field1.name == field2.name, "name полей не совпадают"
        assert field1.hint == field2.hint, "hint полей не совпадают"
        assert field1.type == field2.type, "type полей не совпадают"
        assert field1.length == field2.length, "length полей не совпадают"
        assert field1.mask == field2.mask, "mask полей не совпадают"
        assert field1.value == field2.value, "tag полей не совпадают"

    def _compare_groups(self, group1, group2):
        assert group1.name == group2.name, "Имена групп не совпадают"
        assert len(group1.fields) == len(
            group2.fields
        ), "Размеры групп не совпадают"
        for field1, field2 in zip(group1.fields, group2.fields):
            self._compare_fields(field1, field2)

    def _compare_minified(self, doc1, doc2):
        # id: document_id_type
        assert doc1.description == doc2.description
        assert doc1.template_id == doc2.template_id
        assert doc1.owner_id == doc2.owner_id
        assert doc1.completed == doc2.completed
        # assert doc1.thumbnail == doc2.thumbnail

    def _compare_documents(self, doc1, doc2):
        assert doc1.description == doc2.description
        assert doc1.template_id == doc2.template_id
        assert doc1.owner_id == doc2.owner_id
        assert doc1.completed == doc2.completed
        assert doc1.thumbnail == doc2.thumbnail
        assert len(doc1.grouped_fields) == len(doc2.grouped_fields)
        assert len(doc1.ungrouped_fields) == len(doc2.ungrouped_fields)
        for group1, group2 in zip(doc1.grouped_fields, doc2.grouped_fields):
            self._compare_groups(group1, group2)
        for field1, field2 in zip(
            doc1.ungrouped_fields, doc2.ungrouped_fields
        ):
            self._compare_fields(field1, field2)

    async def _check_document_by_id(self, id, expected_dto: DocumentReadDTO):
        read_dto = await DocumentService.get(id=id)
        assert read_dto, "Объект не найден в базе"
        self._compare_documents(read_dto, expected_dto)

    async def test_get_invalid_id_raises_exception(self):
        with pytest.raises(DocumentNotFoundException):
            await DocumentService.get(id=100)

    @pytest.mark.parametrize(
        "templates, documents_for_write, documents_for_read",
        [(templates_for_write, documents_for_write, documents_for_read)],
    )
    async def test_add_and_delete(
        self,
        templates: dict[str, Any],
        documents_for_write: dict[str, Any],
        documents_for_read: dict[str, Any],
    ):
        # tpl_write_dto = [TemplateWriteDTO(**tpl) for tpl in templates]
        tpl_read_dto = {
            id: await TemplateService.add(TemplateWriteDTO(**tpl))
            for id, tpl in enumerate(templates, start=1)
        }
        print(tpl_read_dto)
        assert False
        # db_len = len(await TemplateService.get_all())
        # new_obj_id = await TemplateService.add(write_dto)
        # assert new_obj_id, "Функция не вернула id нового объекта"
        # new_db_len = len(await TemplateService.get_all())
        # assert db_len + 1 == new_db_len, "Объект не добавлен в базу"

        # # Чтение записи по id из базы
        # expected_dto = TemplateReadDTO(**read_data)
        # await self._check_template_by_id(new_obj_id, expected_dto)

        # # удаление созданной записи
        # await TemplateService.delete(new_obj_id)
        # new_db_len = len(await TemplateService.get_all())
        # assert new_db_len == db_len
        # with pytest.raises(TemplateNotFoundException):
        #     obj_db = await TemplateService.get(id=new_obj_id)
        #     assert not obj_db, "Объект не удален из базы"

        # with pytest.raises(TemplateAlreadyDeletedException):
        #     await TemplateService.delete(id=new_obj_id)
        #     assert (
        #         False
        #     ), "Удаление должно взводить TemplateAlreadyDeletedException"

    # async def test_get_all_and_delete(self):
    #     db_len = len(await TemplateService.get_all())
    #     db_with_deleted_len = len(
    #         await TemplateService.get_all(include_deleted=True)
    #     )
    #     # добавление нескольких объектов в базу
    #     new_obj_ids = []
    #     for write_data in templates_for_write:
    #         write_dto = TemplateWriteDTO(**write_data)
    #         new_id = await TemplateService.add(write_dto)
    #         assert new_id, "Функция не вернула id нового объекта"
    #         new_obj_ids.append(new_id)
    #     new_db_len = len(await TemplateService.get_all())
    #     assert (
    #         db_len + len(templates_for_read) == new_db_len
    #     ), "Объекты не добавлены в базу"

    #     # проверка их наличия в базе
    #     expected_dtos = [TemplateReadDTO(**x) for x in templates_for_read]
    #     for id, expected_dto in zip(new_obj_ids, expected_dtos):
    #         await self._check_template_by_id(id, expected_dto)

    #     # удаление созданных записей
    #     for id in new_obj_ids:
    #         await TemplateService.delete(id)
    #         with pytest.raises(TemplateNotFoundException):
    #             obj_db = await TemplateService.get(id=id)
    #             assert not obj_db, "Объект не удален из базы"
    #     # проверка количества записей в б.д.
    #     new_db_len = len(await TemplateService.get_all())
    #     new_db_with_deleted_len = len(
    #         await TemplateService.get_all(include_deleted=True)
    #     )
    #     assert (
    #         db_len == new_db_len
    #     ), "Кол-во записей в б.д. не соответствует ожидаемым"
    #     assert new_db_with_deleted_len == db_with_deleted_len + len(
    #         new_obj_ids
    #     )

    # async def test_post_invalid_type_raises_exception(self):
    #     new_obj = TemplateWriteDTO(**template_with_invalid_type_field)
    #     with pytest.raises(TypeFieldNotFoundException):
    #         new_id = await TemplateService.add(new_obj)
    #         assert new_id, "Создан объект с ошибочным типом"

    # async def test_delete_invalid_id_raises_exception(self):
    #     with pytest.raises(TemplateNotFoundException):
    #         await TemplateService.delete(id=100)
