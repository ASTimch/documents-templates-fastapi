from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import Sequence
from app.database import async_session_maker

# mock for dao and db
from app.models.template import (
    TemplateFieldType,
    TemplateFieldGroup,
    TemplateField,
    Template,
)
from app.schemas.template import TemplateRead, TemplateReadMinified

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
