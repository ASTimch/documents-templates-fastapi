from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import Sequence
from app.common.constants import Messages

from app.common.exceptions import (
    TypeFieldAlreadyExistsException,
    TypeFieldNotFoundException,
)
from app.crud.template_dao import TemplateFieldTypeDAO
from app.database import async_session_maker, idpk

from app.models.template import (
    Template,
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
)
from app.schemas.template import (
    TemplateFieldTypeAddDTO,
    TemplateFieldTypeReadDTO,
    TemplateRead,
    TemplateReadMinified,
)


# mock for dao and db
groups = [
    TemplateFieldGroup(id=1, name="Группа 1.1", template_id=1),
    TemplateFieldGroup(id=2, name="Группа 1.2", template_id=1),
    TemplateFieldGroup(id=3, name="Группа 2.1", template_id=2),
    TemplateFieldGroup(id=4, name="Группа 2.2", template_id=2),
]
field_types = [
    TemplateFieldType(id=1, type="str", name="Строка"),
    TemplateFieldType(id=2, type="date", name="Дата"),
    TemplateFieldType(id=3, type="int", name="Целое"),
    TemplateFieldType(id=4, type="time", name="Время"),
]
template_fields = [
    TemplateField(
        id=1,
        tag="tag1",
        name="name1",
        hint="hint1",
        type_id=1,
        group_id=1,
        template_id=1,
    ),
    TemplateField(
        id=2,
        tag="tag2",
        name="name2",
        hint="hint2",
        type_id=2,
        group_id=1,
        template_id=1,
    ),
    TemplateField(
        id=3,
        tag="tag3",
        name="name3",
        hint="hint3",
        type_id=3,
        group_id=2,
        template_id=1,
    ),
    TemplateField(
        id=4,
        tag="tag4",
        name="name4",
        hint="hint4",
        type_id=4,
        group_id=2,
        template_id=1,
    ),
    TemplateField(
        id=5,
        tag="tag5",
        name="name5",
        hint="hint5",
        type_id=1,
        group_id=3,
        template_id=2,
    ),
    TemplateField(
        id=6,
        tag="tag6",
        name="name6",
        hint="hint6",
        type_id=2,
        group_id=3,
        template_id=2,
    ),
    TemplateField(
        id=7,
        tag="tag7",
        name="name7",
        hint="hint7",
        type_id=3,
        group_id=4,
        template_id=2,
    ),
    TemplateField(
        id=8,
        tag="tag8",
        name="name8",
        hint="hint8",
        type_id=4,
        group_id=4,
        template_id=2,
    ),
]
templates_mock = [
    Template(
        id=1,
        title="Шаблон1",
        description="Описание1",
        filename="tpl1.docx",
        thumbnail="./thumb1.png",
        deleted=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    ),
    Template(
        id=2,
        title="Шаблон2",
        description="Описание2",
        filename="tpl2.docx",
        thumbnail="./thumb2.png",
        deleted=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    ),
]


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
    async def add(
        cls, obj: TemplateFieldTypeAddDTO
    ) -> Optional[TemplateFieldTypeReadDTO]:
        """Добавить новый объект"""

        obj_db = await TemplateFieldTypeDAO.get_one_or_none(type=obj.type)
        if obj_db:
            raise TypeFieldAlreadyExistsException(
                detail=Messages.TYPE_FIELD_ALREADY_EXISTS.format(obj.type)
            )
        obj_db = await TemplateFieldTypeDAO.create(**obj.model_dump())
        return TemplateFieldTypeReadDTO.model_validate(obj_db)

    @classmethod
    async def add_list(
        cls, obj_list: list[TemplateFieldTypeAddDTO]
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
        cls, id: idpk, obj: TemplateFieldTypeAddDTO
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


class TemplateService:
    @classmethod
    async def get(cls, *, id: int) -> Optional[TemplateRead]:
        async with async_session_maker() as db:
            if id <= 0 or id >= len(templates_mock):
                raise HTTPException(status_code=404, detail="Not found")
            obj = templates_mock[id]
            obj_groups = obj.groups
            print(obj_groups)
            schema = TemplateRead.model_validate(obj)

            return schema

            # api = await ApiDao.get(db, pk)
            # if not api:
            #     raise errors.NotFoundError(msg='接口不存在')
            # return api

    # @classmethod
    # async def get_select(
    #     *, name: str = None, method: str = None, path: str = None
    # ) -> Select:
    #     return await ApiDao.get_list(name=name, method=method, path=path)

    @classmethod
    async def get_all(cls) -> Sequence[TemplateReadMinified]:
        async with async_session_maker() as db:
            # print(templates[0].to_dict())
            # print(templates[1].to_dict())
            # print(templates[0].model_dump())
            # apis = await ApiDao.get_all(db)
            templates = [
                TemplateReadMinified.model_validate(tpl)
                for tpl in templates_mock
            ]
            return templates
            # return apis

    # @classmethod
    # async def create(*, obj: CreateApi) -> None:
    #     async with async_db_session.begin() as db:
    #         api = await ApiDao.get_by_name(db, obj.name)
    #         if api:
    #             raise errors.ForbiddenError(msg="接口已存在")
    #         await ApiDao.create(db, obj)

    # @classmethod
    # async def update(*, pk: int, obj: UpdateApi) -> int:
    #     async with async_db_session.begin() as db:
    #         count = await ApiDao.update(db, pk, obj)
    #         return count

    # @classmethod
    # async def delete(*, pk: list[int]) -> int:
    #     async with async_db_session.begin() as db:
    #         count = await ApiDao.delete(db, pk)
    #         return count
