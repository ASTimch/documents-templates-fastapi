from typing import Any

import pytest
import sqlalchemy
from icecream import ic  # noqa

from app.common.exceptions import (
    DocumentAccessDeniedException,
    DocumentConflictException,
    DocumentNotFoundException,
)
from app.config import settings
from app.crud.base_dao import UserDAO
from app.database import async_session_maker
from app.models.document import Document, DocumentField
from app.models.template import Template, TemplateField
from app.models.user import User
from app.schemas.document import (
    DocumentReadDTO,
    DocumentReadMinifiedDTO,
    DocumentWriteDTO,
)
from app.schemas.template import TemplateWriteDTO
from app.services.document import DocumentService
from app.services.template import TemplateService
from app.tests.fixtures import (
    documents_for_read,
    documents_for_write,
    inconsistent_documents,
    templates_for_read,
)

# users_ids
active_user_id = 1
admin_user_id = 2
inactive_user_id = 3


@pytest.fixture(autouse=True, scope="class")
async def active_user():
    return await UserDAO.get_by_id(active_user_id)


@pytest.fixture(autouse=True, scope="class")
async def admin_user():
    return await UserDAO.get_by_id(admin_user_id)


@pytest.fixture(autouse=True, scope="class")
async def inactive_user():
    return await UserDAO.get_by_id(inactive_user_id)


@pytest.fixture(autouse=True, scope="class")
async def prepare_templates():
    assert settings.MODE == "TEST"

    async with async_session_maker() as session:
        # await session.execute(sqlalchemy.delete(Template))
        # await session.execute(sqlalchemy.delete(TemplateField))
        await session.execute(Template.__table__.delete())
        await session.execute(TemplateField.__table__.delete())
        await session.execute(Document.__table__.delete())
        await session.execute(DocumentField.__table__.delete())
        # await session.execute(
        #     text(
        #         f"SELECT SETVAL('{table_name}_id_seq',"
        #         f" COALESCE((SELECT MAX(id) FROM {table_name}),1));"
        #     )
        # )
        # reset template.id and template_field.id
        await session.execute(
            sqlalchemy.text("ALTER SEQUENCE template_id_seq RESTART;")
        )
        await session.execute(
            sqlalchemy.text("ALTER SEQUENCE template_field_id_seq RESTART;")
        )
        await session.commit()
    for id, tpl in enumerate(templates_for_read, start=1):
        assert id == await TemplateService.add(TemplateWriteDTO(**tpl))


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
        # assert doc1.thumbnail == doc2.thumbnail
        assert len(doc1.grouped_fields) == len(doc2.grouped_fields)
        assert len(doc1.ungrouped_fields) == len(doc2.ungrouped_fields)
        for group1, group2 in zip(doc1.grouped_fields, doc2.grouped_fields):
            self._compare_groups(group1, group2)
        for field1, field2 in zip(
            doc1.ungrouped_fields, doc2.ungrouped_fields
        ):
            self._compare_fields(field1, field2)

    async def _check_document_by_id(
        self, id, expected_dto: DocumentReadDTO, user: User
    ):
        read_dto = await DocumentService.get(id=id, user=user)
        assert read_dto, "Объект не найден в базе"
        self._compare_documents(read_dto, expected_dto)

    async def test_get_invalid_id_raises_exception(self, active_user):
        with pytest.raises(DocumentNotFoundException):
            await DocumentService.get(id=100, user=active_user)

    async def test_delete_invalid_id_raises_exception(self, active_user):
        with pytest.raises(DocumentNotFoundException):
            await DocumentService.delete(id=100, user=active_user)

    @pytest.mark.parametrize(
        "documents_for_write, documents_for_read",
        [(documents_for_write, documents_for_read)],
    )
    async def test_add_get_delete(
        self,
        documents_for_write: dict[str, Any],
        documents_for_read: dict[str, Any],
        active_user,
        admin_user,
        inactive_user,
    ):
        # create documents for simple User
        doc_ids = [
            await DocumentService.add(DocumentWriteDTO(**doc), active_user)
            for doc in documents_for_write
        ]

        for id, doc_read in zip(doc_ids, documents_for_read):
            expected_dto = DocumentReadDTO(**doc_read)
            await self._check_document_by_id(id, expected_dto, active_user)

        # check no access for no author
        for id in doc_ids:
            with pytest.raises(DocumentAccessDeniedException):
                await DocumentService.get(id=id, user=admin_user)

        # get_all for active_user
        user_docs = await DocumentService.get_all(active_user)
        for doc_dto, expected_doc in zip(user_docs, documents_for_read):
            expected_dto = DocumentReadMinifiedDTO(**expected_doc)
            self._compare_minified(doc_dto, expected_dto)

        # get_all for admin_user
        admin_docs = await DocumentService.get_all(admin_user)
        assert not admin_docs, "У администратора нет документов."

        # delete documents by not owner
        for id in doc_ids:
            with pytest.raises(DocumentAccessDeniedException):
                await DocumentService.delete(id, admin_user)

        # delete documents by owner
        for id in doc_ids:
            await DocumentService.delete(id, active_user)
            with pytest.raises(DocumentNotFoundException):
                await DocumentService.get(id=id, user=active_user)

    @pytest.mark.parametrize("documents", (inconsistent_documents,))
    async def test_add_raises_exception_for_inconsistent_request(
        self,
        documents: dict[str, Any],
        active_user,
    ):
        # create documents for simple User
        for doc in documents:
            with pytest.raises(DocumentConflictException):
                await DocumentService.add(DocumentWriteDTO(**doc), active_user)

    @pytest.mark.parametrize(
        "documents_for_write, documents_for_read",
        [(documents_for_write, documents_for_read)],
    )
    async def test_get_all_filter_by(
        self,
        documents_for_write: dict[str, Any],
        documents_for_read: dict[str, Any],
        active_user,
    ):
        # create documents for simple User
        doc_ids = [
            await DocumentService.add(DocumentWriteDTO(**doc), active_user)
            for doc in documents_for_write
        ]

        # get_all completed documents
        user_docs = await DocumentService.get_all(active_user, completed=True)
        assert user_docs, "Должны быть документы с completed=True"
        for doc_dto in user_docs:
            assert doc_dto.completed is True, "Ошибка выборки"

        # get_all not completed documents (drafts)
        user_docs = await DocumentService.get_all(active_user, completed=False)
        assert user_docs, "Должны быть документы с completed=False"
        for doc_dto in user_docs:
            assert doc_dto.completed is False, "Ошибка выборки"

        # delete documents by owner
        for id in doc_ids:
            await DocumentService.delete(id, active_user)

    @pytest.mark.parametrize("documents_for_write", (documents_for_write,))
    async def test_add_for_inactive_user(
        self,
        documents_for_write: dict[str, Any],
        inactive_user,
    ):
        # create documents for inactive_user should raise AccessDenied
        for doc in documents_for_write:
            with pytest.raises(DocumentAccessDeniedException):
                await DocumentService.add(
                    DocumentWriteDTO(**doc), inactive_user
                )
