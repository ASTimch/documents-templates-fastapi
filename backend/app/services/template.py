from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import aiofiles.os
from fastapi import UploadFile
from sqlalchemy import Sequence

from app.common.constants import Messages
from app.common.exceptions import (
    TemplateAlreadyDeletedException,
    TemplateNotFoundException,
    TypeFieldNotFoundException,
)
from app.config import settings
from app.crud.template_dao import (
    TemplateDAO,
    TemplateFieldDAO,
    TemplateFieldGroupDAO,
    TemplateFieldTypeDAO,
)
from app.database import async_session_maker, idpk
from app.models.template import (
    Template,
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
)
from app.schemas.template import (
    TemplateFieldTypeReadDTO,
    TemplateFieldTypeWriteDTO,
    TemplateReadDTO,
    TemplateReadMinifiedDTO,
    TemplateWriteDTO,
)
from app.services.docx_render import DocxRender
from app.services.template_field_type import TemplateFieldTypeService

# mock for dao and db
# groups = [
#     TemplateFieldGroup(id=1, name="Группа 1.1", template_id=1),
#     TemplateFieldGroup(id=2, name="Группа 1.2", template_id=1),
#     TemplateFieldGroup(id=3, name="Группа 2.1", template_id=2),
#     TemplateFieldGroup(id=4, name="Группа 2.2", template_id=2),
# ]
# field_types = [
#     TemplateFieldType(id=1, type="str", name="Строка"),
#     TemplateFieldType(id=2, type="date", name="Дата"),
#     TemplateFieldType(id=3, type="int", name="Целое"),
#     TemplateFieldType(id=4, type="time", name="Время"),
# ]
# template_fields = [
#     TemplateField(
#         id=1,
#         tag="tag1",
#         name="name1",
#         hint="hint1",
#         type_id=1,
#         group_id=1,
#         template_id=1,
#     ),
#     TemplateField(
#         id=2,
#         tag="tag2",
#         name="name2",
#         hint="hint2",
#         type_id=2,
#         group_id=1,
#         template_id=1,
#     ),
#     TemplateField(
#         id=3,
#         tag="tag3",
#         name="name3",
#         hint="hint3",
#         type_id=3,
#         group_id=2,
#         template_id=1,
#     ),
#     TemplateField(
#         id=4,
#         tag="tag4",
#         name="name4",
#         hint="hint4",
#         type_id=4,
#         group_id=2,
#         template_id=1,
#     ),
#     TemplateField(
#         id=5,
#         tag="tag5",
#         name="name5",
#         hint="hint5",
#         type_id=1,
#         group_id=3,
#         template_id=2,
#     ),
#     TemplateField(
#         id=6,
#         tag="tag6",
#         name="name6",
#         hint="hint6",
#         type_id=2,
#         group_id=3,
#         template_id=2,
#     ),
#     TemplateField(
#         id=7,
#         tag="tag7",
#         name="name7",
#         hint="hint7",
#         type_id=3,
#         group_id=4,
#         template_id=2,
#     ),
#     TemplateField(
#         id=8,
#         tag="tag8",
#         name="name8",
#         hint="hint8",
#         type_id=4,
#         group_id=4,
#         template_id=2,
#     ),
# ]
# templates_mock = [
#     Template(
#         id=1,
#         title="Шаблон1",
#         description="Описание1",
#         filename="tpl1.docx",
#         thumbnail="./thumb1.png",
#         deleted=False,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow(),
#     ),
#     Template(
#         id=2,
#         title="Шаблон2",
#         description="Описание2",
#         filename="tpl2.docx",
#         thumbnail="./thumb2.png",
#         deleted=False,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow(),
#     ),
# ]


class TemplateService:
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
        """Назначение всем элементам из fields родительского шаблона template_id"""
        for field in fields:
            field["template_id"] = template_id

    @classmethod
    async def add(cls, obj: TemplateWriteDTO) -> Optional[int]:
        """Добавить новый шаблон

        :return: id созданного объекта шаблон
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
    async def get_or_raise_not_found(cls, id: int) -> Optional[Template]:
        obj = await TemplateDAO.get_by_id(id)
        if not obj or obj.deleted:
            raise TemplateNotFoundException()
        return obj

    @classmethod
    async def get(cls, *, id: int) -> Optional[TemplateReadDTO]:
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
        return TemplateReadDTO.model_validate(obj_dict)

    # @classmethod
    # async def get_select(
    #     *, name: str = None, method: str = None, path: str = None
    # ) -> Select:
    #     return await ApiDao.get_list(name=name, method=method, path=path)

    @classmethod
    async def get_all(
        cls, include_deleted=False
    ) -> Sequence[TemplateReadMinifiedDTO]:
        """Получить все шаблоны в сокращенном виде (без описания полей)"""
        if include_deleted:
            obj_sequence = await TemplateDAO.get_all()
        else:
            obj_sequence = await TemplateDAO.get_all(deleted=False)
        obj_dto_list = [
            TemplateReadMinifiedDTO.model_validate(obj) for obj in obj_sequence
        ]
        return obj_dto_list

    # @classmethod
    # async def update(*, pk: int, obj: UpdateApi) -> int:
    #     async with async_db_session.begin() as db:
    #         count = await ApiDao.update(db, pk, obj)
    #         return count

    @classmethod
    async def update_docx_template(cls, id: int, file: UploadFile) -> None:
        obj_db = await cls.get_or_raise_not_found(id)
        # force change file name to proper format tpl_<id>.docx
        file.filename = f"tpl_{obj_db.id}.docx"
        if obj_db.filename and obj_db.filename.name != file.filename:
            # delete old file if it has different name
            await aiofiles.os.remove(obj_db.filename.path)
        await TemplateDAO.update_(obj_db.id, filename=file)

        # manual saving without fastapi-storage
        # docx_file_name = settings.TEMPLATE_DOCX_DIR + f"tpl_{obj_db.id}.docx"
        # async with aiofiles.open(docx_file_name, "wb") as out_file:
        #     while content := await file.read(1024):
        #         await out_file.write(content)
        # await TemplateDAO.update_(obj_db.id, filename=docx_file_name)

    @classmethod
    async def delete(cls, id: idpk) -> int:
        """Удалить шаблон с заданным id"""

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

        :returns: (excess_tags, excess_fields)
        excess_tags - тэги, которые имеются в docx, но отсутствуют в БД
        excess_fields - тэги, которые имеются в БД, но отсутствуют в docx
        """
        tpl = await cls.get_or_raise_not_found(id)
        docx_tags, field_tags = set(), set()
        if tpl.filename:
            try:
                doc = DocxRender(tpl.filename)
                docx_tags = set(doc.get_tags())
            except Exception as e:
                print(e)  # TODO: add logging

        field_tags = {field.tag for field in tpl.fields}
        excess_tags = tuple(docx_tags - field_tags)
        excess_fields = tuple(field_tags - docx_tags)
        return (excess_tags, excess_fields)

    @classmethod
    async def get_consistency_errors(cls, id: idpk) -> List[Dict[str, str]]:
        """Проверка согласованности тэгов в docx файле и полях базы данных"""

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
