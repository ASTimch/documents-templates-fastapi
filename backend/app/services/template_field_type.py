from typing import Optional

from app.common.constants import Messages
from app.common.exceptions import (
    TypeFieldAlreadyExistsException,
    TypeFieldNotFoundException,
)
from app.crud.template_dao import TemplateFieldTypeDAO
from app.models.base import pk_type
from app.schemas.template import (
    TemplateFieldTypeReadDTO,
    TemplateFieldTypeWriteDTO,
)


class TemplateFieldTypeService:
    @classmethod
    async def get(cls, *, id: pk_type) -> Optional[TemplateFieldTypeReadDTO]:
        """Возвращает тип поля с заданным идентификатором.

        Args:
            id (pk_type): идентификатор объекта в БД.

        Returns:
            TemplateFieldTypeReadDTO: описание типа с заданным id.

        Raises:
            TypeFieldNotFoundException: если тип с заданным id не найден.
        """

        obj = await TemplateFieldTypeDAO.get_by_id(id)
        if not obj:
            raise TypeFieldNotFoundException()
        return TemplateFieldTypeReadDTO.model_validate(obj)

    @classmethod
    async def get_all(cls) -> list[TemplateFieldTypeReadDTO]:
        """Возвращает все типы полей из БД.

        Returns:
            list[TemplateFieldTypeReadDTO]: список типов полей.
        """

        obj_sequence = await TemplateFieldTypeDAO.get_all()
        return [
            TemplateFieldTypeReadDTO.model_validate(obj)
            for obj in obj_sequence
        ]

    @classmethod
    async def get_all_type_id_mapping(cls) -> Optional[dict[str, pk_type]]:
        """Получить словарь соответствия {type: id} для всех типов."""
        obj_sequence = await TemplateFieldTypeDAO.get_all()
        return {obj.type: obj.id for obj in obj_sequence}

    @classmethod
    async def add(
        cls, obj: TemplateFieldTypeWriteDTO
    ) -> Optional[TemplateFieldTypeReadDTO]:
        """Добавить новый тип в БД.

        Args:
            obj (TemplateFieldTypeWriteDTO): описание нового типа.

        Returns:
            TemplateFieldTypeReadDTO: описание добавленного типа.

        Raises:
            TypeFieldAlreadyExistsException: если тип уже существует.
        """

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
        """Добавить все объекты из списка obj_list.

        Args:
            obj_list (list[TemplateFieldTypeWriteDTO]): список новых типов.

        Returns:
            list[TemplateFieldTypeReadDTO]: список добавленных типов.

        Raises:
            TypeFieldAlreadyExistsException: при попытке добавить тип,
            который уже существует.
        """
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
        cls, id: pk_type, obj: TemplateFieldTypeWriteDTO
    ) -> TemplateFieldTypeReadDTO:
        """Обновить объект с заданным идентификатором.

        Args:
            id (pk_type): идентификатор обновляемого объекта.
            obj (TemplateFieldTypeWriteDTO): значения обновляемых полей.

        Returns:
            TemplateFieldTypeReadDTO: обновленный объект.

        Raises:
            TypeFieldNotFoundException: если объект с заданным id не найден.
            TypeFieldAlreadyExistsException: при попытке создать тип с
            дублирующим наименованием.
        """

        obj_by_id = await TemplateFieldTypeDAO.get_by_id(id)
        if not obj_by_id:
            raise TypeFieldNotFoundException(
                detail=Messages.TYPE_FIELD_NOT_FOUND.format(id)
            )
        obj_by_type = await TemplateFieldTypeDAO.get_one_or_none(type=obj.type)
        if obj_by_type and obj_by_type.id != id:
            raise TypeFieldAlreadyExistsException(
                detail=Messages.TYPE_FIELD_ALREADY_EXISTS.format(obj.type)
            )
        obj_by_id = await TemplateFieldTypeDAO.update_(id, **obj.model_dump())
        return obj_by_id

    @classmethod
    async def delete(cls, id: pk_type):
        """Удалить объект с заданным идентификатором.

        Args:
            id (pk_type): идентификатор удаляемого объекта.

        Raises:
            TypeFieldNotFoundException: если объект с заданным id не найден.

        """
        obj_db = await TemplateFieldTypeDAO.get_by_id(id)
        if not obj_db:
            raise TypeFieldNotFoundException(
                detail=Messages.TYPE_FIELD_NOT_FOUND.format(id)
            )
        await TemplateFieldTypeDAO.delete_(id)
