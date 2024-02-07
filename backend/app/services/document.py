from typing import List, Optional

from app.common.exceptions import (
    DocumentAccessDeniedException,
    DocumentNotFoundException,
)
from app.config import settings
from app.crud.document_dao import DocumentDAO
from app.models.base import pk_type
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentReadDTO, DocumentReadMinifiedDTO


class DocumentService:
    DOCX_FILENAME_FORMAT = "tpl_{id}.docx"
    THUMBNAIL_FILENAME_FORMAT = "thumbnail_{id}.png"
    PREVIEW_FILENAME_FORMAT = "{name}_preview.{ext}"
    THUMBNAIL_WIDTH = settings.THUMBNAIL_WIDTH
    THUMBNAIL_HEIGHT = settings.THUMBNAIL_HEIGHT

    # @classmethod
    # async def add(cls, obj: TemplateWriteDTO) -> Optional[pk_type]:
    #     """Добавить новый шаблон в б.д.

    #     Returns:
    #         pk_type: идентификатор созданного объекта шаблон.
    #     """
    #     type_id_mapping = (
    #         await TemplateFieldTypeService.get_all_type_id_mapping()
    #     )
    #     obj_dict = obj.model_dump()
    #     group_dicts = obj_dict.pop("grouped_fields")
    #     field_dicts = obj_dict.pop("ungrouped_fields")
    #     for group in group_dicts:
    #         cls._update_fields_type_by_id(group["fields"], type_id_mapping)
    #     cls._update_fields_type_by_id(field_dicts, type_id_mapping)

    #     # создание шаблона (без полей)
    #     template = await TemplateDAO.create(**obj_dict)
    #     # создание групп полей
    #     for group in group_dicts:
    #         cls._update_fields_template_id(group["fields"], template.id)
    #         group["fields"] = await TemplateFieldDAO.create_list(
    #             group["fields"]
    #         )
    #         group["template_id"] = template.id
    #     await TemplateFieldGroupDAO.create_list(group_dicts)
    #     # создание несгруппированных полей
    #     cls._update_fields_template_id(field_dicts, template.id)
    #     await TemplateFieldDAO.create_list(field_dicts)
    #     return template.id

    @classmethod
    async def get_or_raise_not_found(cls, id: pk_type) -> Optional[Document]:
        """Поиск документа по идентификатору.

        Args:
            id (pk_type): идентификатор документа.

        Returns:
            Document: объект документа с заданным id.

        Raises:
            DocumentNotFoundException: если объект с заданным id
            отсутствует.
        """
        obj = await DocumentDAO.get_by_id(id)
        if not obj:
            raise DocumentNotFoundException()
        return obj

    @classmethod
    async def get(
        cls, *, id: pk_type, user: Optional[User] = None
    ) -> Optional[DocumentReadDTO]:
        """Возвращает документ с заданным id с описанием всех его полей.

        Args:
            id (int): идентификатор документа в б.д.
            user(User): пользователь для которого генерируется ответ.

        Returns:
            DocumentReadDTO: документ со всеми полями и их описанием.

        Raises:
            DocumentNotFoundException: документ с заданным id не найден.
            DocumentAccessDeniedException: неавторизованный доступ.
        """
        obj = await cls.get_or_raise_not_found(id)
        # запрет доступа всем, кроме владельца документа
        if obj.owner_id != user.id:
            raise DocumentAccessDeniedException()
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
            field_dict["value"] = field_values.get(field.id, None)
            group_dict = groups_dicts.get(field.group_id)
            if group_dict:
                group_dict.setdefault("fields", []).append(field_dict)
            else:
                ungrouped_fields.append(field_dict)
        obj_dict = obj.to_dict()
        obj_dict["grouped_fields"] = groups_dicts.values()
        obj_dict["ungrouped_fields"] = ungrouped_fields
        return DocumentReadDTO.model_validate(obj_dict)

    @classmethod
    async def get_all(
        cls, user: Optional[User] = None
    ) -> List[DocumentReadMinifiedDTO]:
        """Возвращает все документы пользователя в сокращенном виде
        (без описания полей).

        Args:
            user (User): пользователь автор документов.

        Returns:
            list[DocumentReadMinifiedDTO]: список документов.
        """
        if not user:
            return []
        obj_sequence = await DocumentDAO.get_all(owner_id=user.id)
        return [
            DocumentReadMinifiedDTO.model_validate(obj) for obj in obj_sequence
        ]
