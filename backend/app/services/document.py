import logging
from io import BytesIO
from typing import Any, List, Optional, Tuple

from app.common.constants import Messages
from app.common.exceptions import (
    DocumentAccessDeniedException,
    DocumentConflictException,
    DocumentNotFoundException,
    TemplateNotFoundException,
    TemplatePdfConvertErrorException,
    TemplateRenderErrorException,
)
from app.config import settings
from app.crud.document_dao import DocumentDAO, DocumentFieldDAO
from app.models.base import pk_type
from app.models.document import Document
from app.models.user import User
from app.schemas.document import (
    DocumentReadDTO,
    DocumentReadMinifiedDTO,
    DocumentWriteDTO,
)
from app.services.docx_render import DocxRender
from app.services.pdf_converter import PdfConverter
from app.services.template import TemplateService

# from icecream import ic


logger = logging.getLogger(__name__)


class DocumentService:
    DOCX_FILENAME_FORMAT = "tpl_{id}.docx"
    THUMBNAIL_FILENAME_FORMAT = "thumbnail_{id}.png"
    PREVIEW_FILENAME_FORMAT = "{name}_preview.{ext}"
    THUMBNAIL_WIDTH = settings.THUMBNAIL_WIDTH
    THUMBNAIL_HEIGHT = settings.THUMBNAIL_HEIGHT

    @classmethod
    async def _check_document_consistency(cls, dto: DocumentWriteDTO) -> None:
        """Проверка согласованности полей в запросе создания документа.

        Все поля должны принадлежать заданному существующему шаблону.

        Args:
            dto (DocumentWriteDTO): объект для создания документа.

        Raises:
            DocumentConflictException: несогласованность полей.
        """
        # проверка, что шаблон с заданным template_id существут
        try:
            tpl_obj = await TemplateService.get_or_raise_not_found(
                dto.template_id
            )
        except TemplateNotFoundException:
            raise DocumentConflictException(
                detail=Messages.TEMPLATE_ID_NOT_FOUND.format(dto.template_id)
            )
        # проверка, что все поля принадлежат этому шаблону
        tpl_field_ids = {field.id for field in tpl_obj.fields}
        if wrong_field_ids := [
            field.field_id
            for field in dto.fields
            if field.field_id not in tpl_field_ids
        ]:
            raise DocumentConflictException(
                detail=Messages.DOCUMENT_WRONG_FIELDS.format(
                    fields=wrong_field_ids, tpl=dto.template_id
                )
            )

    @classmethod
    def _update_fields_document_id(
        cls, fields: list[dict[str, Any]], document_id: pk_type
    ) -> list[dict[str, Any]]:
        """Назначение всем полям родительского документа document_id.

        Args:
            fields (list[dict]): Список описаний полей вида:
                {'field_id':<идентификатор поля>, "value": <значение>}
            document_id (pk_type): Идентификатор родительского документа.

        Returns:
            Преобразованный список полей. Исключены все поля с "value"=None
            Каждый элемент fields преобразуется к виду::

            {
                "template_field_id":<идентификатор поля>,
                "value": <значение>,
                "document_id": document_id
            }
        """
        updated_fields = []
        for field in fields:
            field["template_field_id"] = field.pop("field_id")
            field["document_id"] = document_id
            if field["value"] is not None:
                updated_fields.append(field)
        return updated_fields

    @classmethod
    def _model_as_dto(cls, obj: Document) -> DocumentReadDTO:
        """Преобразование модели документа в DTO для выдачи.

        Args:
            obj: Объект модели документа.

        Returns:
            Объект типа DocumentReadDto.
        """
        groups_dicts = {
            group.id: group.to_dict() for group in obj.template.groups
        }
        field_values = {
            field.template_field_id: field.value for field in obj.fields
        }
        ungrouped_fields = []
        for field in obj.template.fields:
            field_dict = field.to_dict()
            field_dict["type"] = field.type.type
            field_dict["mask"] = field.type.mask
            field_dict["value"] = field_values.get(field.id, "")
            group_dict = groups_dicts.get(field.group_id)
            if group_dict:
                group_dict.setdefault("fields", []).append(field_dict)
            else:
                ungrouped_fields.append(field_dict)
        obj_dict = obj.to_dict()
        obj_dict["template_title"] = obj.template.title
        obj_dict["grouped_fields"] = groups_dicts.values()
        obj_dict["ungrouped_fields"] = ungrouped_fields
        return DocumentReadDTO.model_validate(obj_dict)

    @classmethod
    async def add(
        cls, dto: DocumentWriteDTO, owner: User
    ) -> Optional[pk_type]:
        """Сохранить новый документ.

        Args:
            dto: Объект документа для записи.
            owner: Объект пользователя владельца документа.

        Returns:
            pk_type: идентификатор созданного объекта документ.

        Raises:
            DocumentAccessDeniedException: если пользователь деактивирован.
            DocumentConflictException: при несогласованности в полях документа.
        """
        # запрет создания документа для неактивных пользователей
        if not owner.is_active:
            raise DocumentAccessDeniedException()
        # проверка консистентности (template_id и field_id)
        await cls._check_document_consistency(dto)

        obj_dict = dto.model_dump()
        obj_dict["owner_id"] = owner.id
        fields = obj_dict.pop("fields")
        # создание документа (без полей)
        document = await DocumentDAO.create(**obj_dict)
        # создание полей
        fields = cls._update_fields_document_id(fields, document.id)
        await DocumentFieldDAO.create_list(fields)
        return document.id

    @classmethod
    async def get_or_raise_not_found(cls, id: pk_type) -> Optional[Document]:
        """Поиск документа по идентификатору.

        Args:
            id (pk_type): идентификатор документа.

        Returns:
            Document: объект документа с заданным id.

        Raises:
            DocumentNotFoundException: если объект с заданным id отсутствует.
        """
        obj = await DocumentDAO.get_by_id(id)
        if not obj:
            raise DocumentNotFoundException()
        return obj

    @classmethod
    async def get(
        cls, *, id: pk_type, user: User
    ) -> Optional[DocumentReadDTO]:
        """Возвращает документ с заданным id с описанием всех его полей.

        Args:
            id (pk_type): Идентификатор документа в б.д.
            user(User): Пользователь для которого генерируется ответ.

        Returns:
            DocumentReadDTO: Документ со всеми полями и их описанием.

        Raises:
            DocumentNotFoundException: Документ с заданным id не найден.
            DocumentAccessDeniedException: Неавторизованный доступ.
        """
        obj = await cls.get_or_raise_not_found(id)
        # запрет доступа всем, кроме владельца документа
        if obj.owner_id != user.id:
            raise DocumentAccessDeniedException()
        return cls._model_as_dto(obj)

    @classmethod
    async def get_all(
        cls, user: User, **filter_by: Any
    ) -> List[DocumentReadMinifiedDTO]:
        """Возвращает все документы пользователя в сокращенном виде
        (без описания полей).

        Args:
            user (User): пользователь автор документов.
            filter_by: Имена и значения параметров для фильтрации.

        Returns:
            list[DocumentReadMinifiedDTO]: список документов.
        """
        if not user:
            return []
        obj_sequence = await DocumentDAO.get_all(owner_id=user.id, **filter_by)
        return [
            DocumentReadMinifiedDTO.model_validate(
                obj.to_dict() | {"template_title": obj.template.title}
            )
            for obj in obj_sequence
        ]

    @classmethod
    async def delete(cls, id: pk_type, user: User) -> None:
        """Удалить документ с заданным id.

        Args:
            id (pk_type): идентификатор документа.
            user (User): пользователь.

        Raises:
            DocumentNotFoundException: документ с заданным id отсутствует.
            DocumentAccessDeniedException: пользователь не является владельцем.
        """
        obj_db = await DocumentDAO.get_by_id(id)
        if not obj_db:
            raise DocumentNotFoundException()
        if obj_db.owner_id != user.id:
            raise DocumentAccessDeniedException()
        await DocumentDAO.delete_(id)

    @classmethod
    async def update(
        cls, id: pk_type, dto: DocumentWriteDTO, user: User
    ) -> DocumentReadDTO:
        """Изменить/обновить документ.

        Args:
            id (pk_type): Идентификатор документа.
            dto (DocumentWriteDTO): Поля документа.
            user (User): Пользователь.

        Returns:
            DocumentReadDTO: Документ со всеми полями и их описанием.

        Raises:
            DocumentAccessDeniedException: Если пользователь деактивирован
                или не является владельцем документа.
            DocumentNotFoundException: Документ не найден.
            DocumentConflictException: Поля документа не согласованны.
        """
        # запрет модификации документа для неактивных пользователей
        if not user.is_active:
            raise DocumentAccessDeniedException()
        obj_db = await DocumentDAO.get_by_id(id)
        if not obj_db:
            raise DocumentNotFoundException()
        if obj_db.owner_id != user.id:
            raise DocumentAccessDeniedException()
        # проверка консистентности (template_id и field_id)
        await cls._check_document_consistency(dto)
        obj_dict = dto.model_dump()
        obj_dict["owner_id"] = user.id
        fields = obj_dict.pop("fields")
        # обновление свойств документа
        await DocumentDAO.update_(id, **obj_dict)
        # удаление старых полей
        await DocumentFieldDAO.delete_all(document_id=id)
        # создание новых полей
        fields = cls._update_fields_document_id(fields, id)
        await DocumentFieldDAO.create_list(fields)
        document = await DocumentDAO.get_by_id(id)
        return cls._model_as_dto(document)

    @classmethod
    async def get_file(
        cls, id: pk_type, user: User, pdf=False
    ) -> Tuple[BytesIO, str]:
        """Возвращает документ с заполненными полями в формате docx или pdf.

        Args:
            id (pk_type): Идентификатор документа.
            pdf (bool): True для формата pdf, False для формата docx.
            user (User): Пользователь для которого генерируется документ.

        Returns:
            (file (BytesIO), filename (str)): сгенерированный файл и имя.

        Raises:
            DocumentNotFoundException: если документ с заданным id отсутствует.
            DocumentAccessDeniedException: если пользователь не активен или
                не является автором документа.
            TemplateFieldNotFoundException: если field_values содержит
                ошибочные 'field_id', отсутствующие в полях шаблона.
            TemplateRenderErrorException: при ошибках генерации docx.
            TemplatePdfConvertErrorException: при ошибках генерации pdf.

        """
        if not user.is_active:
            raise DocumentAccessDeniedException()
        doc = await cls.get_or_raise_not_found(id)
        if not doc:
            raise DocumentNotFoundException()
        if doc.owner_id != user.id:
            raise DocumentAccessDeniedException()
        field_values = {
            field.template_field_id: field.value
            for field in doc.fields
            if field.value is not None
        }
        context = {
            field.tag: value
            for field in doc.template.fields
            if (value := field_values.get(field.id))
        }
        context_default = {
            field.tag: field.default or field.name
            for field in doc.template.fields
        }
        docx_path = doc.template.filename
        try:
            docx = DocxRender(docx_path)
            buffer = docx.get_partial(context, context_default)
        except Exception as e:
            logger.exception(e)
            raise TemplateRenderErrorException()
        filename = cls.PREVIEW_FILENAME_FORMAT.format(
            name=doc.description, ext="docx"
        )
        if pdf:
            try:
                buffer = PdfConverter.docx_to_pdf(buffer)
                filename = cls.PREVIEW_FILENAME_FORMAT.format(
                    name=doc.description, ext="pdf"
                )
            except Exception as e:
                logging.exception(e)
                raise TemplatePdfConvertErrorException()
        return buffer, filename
