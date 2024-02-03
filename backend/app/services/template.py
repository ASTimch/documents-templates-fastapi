import logging
import urllib
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import aiofiles.os
from fastapi import Response, UploadFile

from app.common.constants import Messages
from app.common.exceptions import (
    TemplateAlreadyDeletedException,
    TemplateFieldNotFoundException,
    TemplateNotFoundException,
    TemplatePdfConvertErrorException,
    TemplateRenderErrorException,
    TypeFieldNotFoundException,
)
from app.config import Settings
from app.crud.template_dao import (
    TemplateDAO,
    TemplateFieldDAO,
    TemplateFieldGroupDAO,
)
from app.database import idpk
from app.models.template import Template
from app.models.user import User
from app.schemas.template import (
    TemplateReadDTO,
    TemplateReadMinifiedDTO,
    TemplateWriteDTO,
)
from app.services.docx_render import DocxRender
from app.services.favorite import TemplateFavoriteService
from app.services.pdf_converter import PdfConverter
from app.services.template_field_type import TemplateFieldTypeService

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, %(levelname)s, %(message)s",
)

logger = logging.getLogger(__name__)


class TemplateService:
    DOCX_FILENAME_FORMAT = "tpl_{id}.docx"
    THUMBNAIL_FILENAME_FORMAT = "thumbnail_{id}.png"
    DRAFT_FILENAME_FORMAT = "{name}_шаблон.{ext}"
    PREVIEW_FILENAME_FORMAT = "{name}_preview.{ext}"
    THUMBNAIL_WIDTH = Settings.THUMBNAIL_WIDTH
    THUMBNAIL_HEIGHT = Settings.THUMBNAIL_HEIGHT

    @classmethod
    def _update_fields_type_by_id(
        cls, fields: list[dict[str, Any]], type_id_mapping: dict[str:int]
    ) -> None:
        """Замена всех наименований типов type соответствующим значением
        type_id из словаря соответствия type_id_mapping"""
        for field in fields:
            field_type = field.pop("type")
            type_id = type_id_mapping.get(field_type)
            if type_id is None:
                raise TypeFieldNotFoundException(
                    detail=Messages.TYPE_FIELD_NOT_FOUND.format(field_type)
                )
            field["type_id"] = type_id

    @classmethod
    def _update_fields_template_id(
        cls, fields: list[dict[str, Any]], template_id: int
    ) -> None:
        """
        Назначение всем элементам из fields родительского шаблона template_id.
        """
        for field in fields:
            field["template_id"] = template_id

    @classmethod
    async def add(cls, obj: TemplateWriteDTO) -> Optional[int]:
        """Добавить новый шаблон в б.д.

        Returns:
            int: идентификатор созданного объекта шаблон.
        """
        type_id_mapping = (
            await TemplateFieldTypeService.get_all_type_id_mapping()
        )
        obj_dict = obj.model_dump()
        group_dicts = obj_dict.pop("grouped_fields")
        field_dicts = obj_dict.pop("ungrouped_fields")
        for group in group_dicts:
            cls._update_fields_type_by_id(group["fields"], type_id_mapping)
        cls._update_fields_type_by_id(field_dicts, type_id_mapping)

        # создание шаблона (без полей)
        template = await TemplateDAO.create(**obj_dict)
        # создание групп полей
        for group in group_dicts:
            cls._update_fields_template_id(group["fields"], template.id)
            group["fields"] = await TemplateFieldDAO.create_list(
                group["fields"]
            )
            group["template_id"] = template.id
        await TemplateFieldGroupDAO.create_list(group_dicts)
        # создание несгруппированных полей
        cls._update_fields_template_id(field_dicts, template.id)
        await TemplateFieldDAO.create_list(field_dicts)
        return template.id

    @classmethod
    async def get_or_raise_not_found(cls, id: idpk) -> Optional[Template]:
        """Поиск шаблона по идентификатору.

        Args:
            id (int): идентификатор шаблона.

        Returns:
            Template: объект шаблона с заданным id.

        Raises:
            TemplateNotFoundException: если объект с заданным id
            отсутствует или удален.
        """
        obj = await TemplateDAO.get_by_id(id)
        if not obj or obj.deleted:
            raise TemplateNotFoundException()
        return obj

    @classmethod
    async def get(
        cls, *, id: idpk, user: Optional[User] = None
    ) -> Optional[TemplateReadDTO]:
        """Возвращает ответ для шаблона с заданным id.

        Args:
            id (int): идентификатор шаблона в б.д.
            user(User): пользователь для которого генерируется ответ.

        Returns:
            TemplateReadDTO: все поля шаблона и описание его полей.

        Raises:
            TemplateNotFoundException: если шаблон с заданным id
            отсутствует или удален.
        """
        obj = await cls.get_or_raise_not_found(id)
        groups_dicts = {group.id: group.to_dict() for group in obj.groups}
        ungrouped_fields = []
        for field in obj.fields:
            field_dict = field.to_dict()
            field_dict["type"] = field.type.type
            field_dict["mask"] = field.type.mask
            group_dict = groups_dicts.get(field.group_id)
            if group_dict:
                fields = group_dict.setdefault("fields", [])
                fields.append(field_dict)
            else:
                ungrouped_fields.append(field_dict)

        obj_dict = obj.to_dict()
        obj_dict["grouped_fields"] = groups_dicts.values()
        obj_dict["ungrouped_fields"] = ungrouped_fields
        # формирование is_favorited (в 'избранном' текущего пользователя)
        if user:
            obj_dict["is_favorited"] = (
                await TemplateFavoriteService.is_favorited(user.id, obj.id)
            )
        return TemplateReadDTO.model_validate(obj_dict)

    # @classmethod
    # async def get_select(
    #     *, name: str = None, method: str = None, path: str = None
    # ) -> Select:
    #     return await ApiDao.get_list(name=name, method=method, path=path)

    @classmethod
    async def get_all(
        cls, user: Optional[User] = None, include_deleted=False
    ) -> List[TemplateReadMinifiedDTO]:
        """Возвращает все шаблоны в сокращенном виде (без описания полей)

        Args:
            user (User): пользователь для которого генерируется ответ.
            include_deleted (bool): включать ли в ответ удаленные шаблоны.

        Returns:
            list[TemplateReadMinifiedDTO]: список доступных шаблонов.
        """
        if include_deleted:
            obj_sequence = await TemplateDAO.get_all()
        else:
            obj_sequence = await TemplateDAO.get_all(deleted=False)
        obj_dto_list = []
        for obj in obj_sequence:
            obj_dto = TemplateReadMinifiedDTO.model_validate(obj)
            if user:
                obj_dto.is_favorited = (
                    await TemplateFavoriteService.is_favorited(user.id, obj.id)
                )
                # TODO: оптимизировать кол-во запросов
                #       один запрос всех избранных шаблонов текущего польз-ля
            obj_dto_list.append(obj_dto)

        return obj_dto_list

    @classmethod
    async def update_docx_template(cls, id: idpk, file: UploadFile) -> None:
        """Обновить docx файл шаблона с заданным id.

        Args:
            id (int): идентификатор шаблона в б.д.
            file(UploadFile): загруженный docx файл шаблона.
        """
        obj_db = await cls.get_or_raise_not_found(id)
        file.filename = cls.DOCX_FILENAME_FORMAT.format(id=obj_db.id)
        if obj_db.filename and obj_db.filename.name != file.filename:
            try:
                await aiofiles.os.remove(obj_db.filename.path)
            except Exception as e:
                logger.exception(e)
        await TemplateDAO.update_(obj_db.id, filename=file)

    @classmethod
    async def generate_thumbnail(cls, template_id: idpk):
        """Генерирует png thumbnail для шаблона документа.

        После генерации обновляет поле thumbnail шаблона в базе данных.

        Args:
            template_id (int): идентификатор шаблона.

        Raises:
            TemplateNotFoundException: если шаблон с заданным template_id
            отсутствует или удален.
        """
        obj_db = await cls.get_or_raise_not_found(template_id)
        pdf_buffer, _ = await TemplateService.get_draft(template_id, pdf=True)
        png_buffer = PdfConverter.pdf_to_thumbnail(
            pdf_buffer,
            width=cls.THUMBNAIL_WIDTH,
            height=cls.THUMBNAIL_HEIGHT,
            format="png",
        )
        filename = cls.THUMBNAIL_FILENAME_FORMAT.format(id=template_id)
        try:
            thumb_file = UploadFile(
                file=png_buffer,
                filename=filename,
                headers={"content-type": "image/png"},
            )
            await TemplateDAO.update_(obj_db.id, thumbnail=thumb_file)
            logger.info(f"Сгенерирован thumbnail: {filename}")
        except Exception as e:
            logger.exception(e)

    @classmethod
    async def delete(cls, id: idpk) -> int:
        """Удалить шаблон с заданным id.

        Args:
            id (int): идентификатор шаблона.

        Raises:
            TemplateNotFoundException: если шаблон с заданным id отсутствует.
            TemplateAlreadyDeletedException: если шаблон уже помечен удаленным.
        """
        obj_db = await TemplateDAO.get_by_id(id)
        if not obj_db:
            raise TemplateNotFoundException()
        if obj_db.deleted:
            raise TemplateAlreadyDeletedException()
        await TemplateDAO.update_(id, deleted=True)

    @classmethod
    async def get_inconsistent_tags(
        cls, id: idpk
    ) -> Tuple[Tuple[str], Tuple[str]]:
        """
        Возвращает списки несогласованных тэгов между БД и шаблоном docx.

        Args:
            id (int): идентификатор шаблона в б.д.

        Returns:
            (excess_tags, excess_fields): кортежи ошибочных тэгов
            excess_tags(tuple[str])): тэги, которые имеются в docx,
            но отсутствуют в БД;
            excess_fields(tuple[str]): тэги, которые имеются в БД,
            но отсутствуют в docx.

        Raises:
            TemplateNotFoundException: если шаблон с заданным id отсутствует.
        """
        tpl = await cls.get_or_raise_not_found(id)
        docx_tags, field_tags = set(), set()
        if tpl.filename:
            try:
                doc = DocxRender(tpl.filename)
                docx_tags = set(doc.get_tags())
            except Exception as e:
                logger.exception(e)

        field_tags = {field.tag for field in tpl.fields}
        excess_tags = tuple(docx_tags - field_tags)
        excess_fields = tuple(field_tags - docx_tags)
        return (excess_tags, excess_fields)

    @classmethod
    async def get_consistency_errors(cls, id: idpk) -> List[Dict[str, str]]:
        """Проверка согласованности тэгов в docx файле и полях базы данных

        Args:
            id (int): идентификатор шаблона в б.д.

        Returns:
            dict[str]: словарь ответа результата проверки шаблона.

        Формат ответа при отсутствии ошибок::

            {"result": <message>}

        Формат ответа при наличии ошибок::

            {"errors":
                [
                    {
                        "message": <сообщение об ошибке>,
                        "tags": <список ошибочных тегов>,
                    },
                ]
            }

        Raises:
            TemplateNotFoundException: если шаблон с заданным id отсутствует.
        """

        excess_tags, excess_fields = await cls.get_inconsistent_tags(id)
        errors = []
        if excess_tags:
            errors.append(
                {"message": Messages.TEMPLATE_EXCESS_TAGS, "tags": excess_tags}
            )
        if excess_fields:
            errors.append(
                {
                    "message": Messages.TEMPLATE_EXCESS_FIELDS,
                    "tags": excess_fields,
                }
            )
        if errors:
            return {"errors": errors}
        return {"result": Messages.TEMPLATE_CONSISTENT}

    @classmethod
    async def get_file_response(
        cls, file: BytesIO, filename: str, pdf: bool = False
    ) -> Response:
        """Формирует и возвращает ответ для отправки файла.

        Args:
            file (BytesIO): файл, который должен быть отправлен.
            filename (str): наименование файла.
            pdf (bool): True для формата pdf, False для формата docx.

        Returns:
            Response: сформированный ответ.
        """
        if pdf:
            media_type = "application/pdf"
        else:
            media_type = "application/docx"
        headers = {
            "Content-Disposition": "attachment; filename*=utf-8''{}".format(
                urllib.parse.quote(filename, encoding="utf-8")
            )
        }
        return Response(
            file.getvalue(), headers=headers, media_type=media_type
        )

    @classmethod
    async def get_draft(cls, id: idpk, pdf=False) -> Tuple[BytesIO, str]:
        """Возвращает черновик документа в формате docx или pdf.

        В черновике все тэги заменены соответствующими наименованиями полей.
        Имя файла filename формируется по полю title шаблона.

        Args:
            id (int): идентификатор шаблона.
            pdf (bool): True для формата pdf, False для формата docx.

        Returns:
            (file (BytesIO), filename (str)): сгенерированный файл и имя.

        Raises:
            TemplateRenderErrorException: при ошибках генерации docx.
            TemplatePdfConvertErrorException: при ошибках генерации pdf.
        """
        tpl = await cls.get_or_raise_not_found(id)
        context = {field.tag: field.name for field in tpl.fields}
        docx_path = tpl.filename.path
        try:
            doc = DocxRender(docx_path)
            buffer = doc.get_draft(context)
        except Exception as e:
            logger.exception(e)
            raise TemplateRenderErrorException
        filename = cls.DRAFT_FILENAME_FORMAT.format(name=tpl.title, ext="docx")
        if pdf:
            try:
                buffer = PdfConverter.docx_to_pdf(buffer)
                filename = cls.DRAFT_FILENAME_FORMAT.format(
                    name=tpl.title, ext="pdf"
                )
            except Exception as e:
                logger.exception(e)
                raise TemplatePdfConvertErrorException
        return buffer, filename

    @classmethod
    async def get_preview(
        cls, id: idpk, field_values: list[dict[int, str]], pdf=False
    ) -> Tuple[BytesIO, str]:
        """Возвращает документ с заполненными полями в формате docx или pdf.

        Args:
            id (int): идентификатор шаблона.
            field_values (list[dict[str]]): список значений полей в виде
            {"field_id":id, "value":значение}
            pdf (bool): True для формата pdf, False для формата docx.

        Returns:
            (file (BytesIO), filename (str)): сгенерированный файл и имя.

        Raises:
            TemplateNotFoundException: если шаблон с заданным id отсутствует.
            TemplateFieldNotFoundException: если field_values содержит
            ошибочные 'field_id', отсутствующие в полях шаблона.
            TemplateRenderErrorException: при ошибках генерации docx.
            TemplatePdfConvertErrorException: при ошибках генерации pdf.
        """

        tpl = await cls.get_or_raise_not_found(id)
        fields_dict = {field.id: field for field in tpl.fields}
        context = {}
        for field_value in field_values:
            field = fields_dict.get(field_value["field_id"])
            if not field:
                raise TemplateFieldNotFoundException(
                    Messages.TEMPLATE_FIELD_NOT_FOUND.format(
                        field_id=field_value["field_id"], template_id=id
                    )
                )
            if field_value["value"]:
                context[field.tag] = field_value["value"]
        context_default = {
            field.tag: field.default or field.name for field in tpl.fields
        }
        docx_path = tpl.filename
        try:
            doc = DocxRender(docx_path)
            buffer = doc.get_partial(context, context_default)
        except Exception as e:
            logger.exception(e)
            raise TemplateRenderErrorException()
        filename = cls.PREVIEW_FILENAME_FORMAT.format(
            name=tpl.title, ext="docx"
        )
        if pdf:
            try:
                buffer = PdfConverter.docx_to_pdf(buffer)
                filename = cls.PREVIEW_FILENAME_FORMAT.format(
                    name=tpl.title, ext="pdf"
                )
            except Exception as e:
                logging.exception(e)
                raise TemplatePdfConvertErrorException()
        return buffer, filename
