from datetime import datetime
from typing import Any, Optional

from app.common.constants import Messages
from app.common.exceptions import (
    TypeFieldAlreadyExistsException,
    TypeFieldNotFoundException,
)
from app.config import settings
from app.crud.template_dao import (
    TemplateFieldTypeDAO,
)
from app.database import idpk
from app.schemas.template import (
    TemplateFieldTypeReadDTO,
    TemplateFieldTypeWriteDTO,
)


class TemplateFieldTypeService:
    @classmethod
    async def get(cls, *, id: idpk) -> Optional[TemplateFieldTypeReadDTO]:
        """Получить объект по заданному id"""

        obj = await TemplateFieldTypeDAO.get_by_id(id)
        if not obj:
            raise TypeFieldNotFoundException()
        return TemplateFieldTypeReadDTO.model_validate(obj)

    @classmethod
    async def get_all(cls) -> list[TemplateFieldTypeReadDTO]:
        """Получить все объекты"""

        obj_sequence = await TemplateFieldTypeDAO.get_all()
        obj_dto_list = [
            TemplateFieldTypeReadDTO.model_validate(obj)
            for obj in obj_sequence
        ]
        return obj_dto_list

    @classmethod
    async def get_all_type_id_mapping(cls) -> Optional[dict[str, int]]:
        """Получить словарь соответствия {type:id}"""
        obj_sequence = await TemplateFieldTypeDAO.get_all()
        type_id_mapping = {obj.type: obj.id for obj in obj_sequence}
        return type_id_mapping

    @classmethod
    async def add(
        cls, obj: TemplateFieldTypeWriteDTO
    ) -> Optional[TemplateFieldTypeReadDTO]:
        """Добавить новый тип"""

        obj_db = await TemplateFieldTypeDAO.get_one_or_none(type=obj.type)
        if obj_db:
            raise TypeFieldAlreadyExistsException(
                detail=Messages.TYPE_FIELD_ALREADY_EXISTS.format(obj.type)
            )
        obj_db = await TemplateFieldTypeDAO.create(**obj.model_dump())
        return TemplateFieldTypeReadDTO.model_validate(obj_db)

    @classmethod
    async def add_list(
        cls, obj_list: list[TemplateFieldTypeWriteDTO]
    ) -> Optional[list[TemplateFieldTypeReadDTO]]:
        """Добавить все объекты из списка obj_list"""

        obj_dict_list = []
        for obj in obj_list:
            obj_by_type = await TemplateFieldTypeDAO.get_one_or_none(
                type=obj.type
            )
            if obj_by_type:
                raise TypeFieldAlreadyExistsException(
                    detail=Messages.TYPE_FIELD_ALREADY_EXISTS.format(obj.type)
                )
            obj_dict_list.append(obj.model_dump())
        created_sequence = await TemplateFieldTypeDAO.create_list(
            obj_dict_list
        )
        return created_sequence

    @classmethod
    async def update(
        cls, id: idpk, obj: TemplateFieldTypeWriteDTO
    ) -> TemplateFieldTypeReadDTO:
        """Обновить объект с заданным id"""

        obj_by_id = await TemplateFieldTypeDAO.get_by_id(id)
        if not obj_by_id:
            raise TypeFieldNotFoundException()
        obj_by_type = await TemplateFieldTypeDAO.get_one_or_none(type=obj.type)
        if obj_by_type and obj_by_type.id != id:
            raise TypeFieldAlreadyExistsException(
                detail=Messages.TYPE_FIELD_ALREADY_EXISTS.format(obj.type)
            )
        obj_by_id = await TemplateFieldTypeDAO.update_(id, **obj.model_dump())
        return obj_by_id

    @classmethod
    async def delete(cls, id: idpk):
        """Удалить объект с заданным id"""

        obj_db = await TemplateFieldTypeDAO.get_by_id(id)
        if not obj_db:
            raise TypeFieldNotFoundException()
        await TemplateFieldTypeDAO.delete_(id)
