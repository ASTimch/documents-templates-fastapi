from typing import Optional

from fastapi import APIRouter, status

from app.database import idpk
from app.schemas.template import (
    TemplateFieldTypeAddDTO,
    TemplateFieldTypeReadDTO,
    TemplateRead,
    TemplateReadMinified,
)
from app.services.template import TemplateFieldTypeService, TemplateService

router = APIRouter()


@router.get("/", summary="Получить все доступные типы полей")
async def get_all_template_field_types() -> Optional[
    list[TemplateFieldTypeReadDTO]
]:
    template_field_types = await TemplateFieldTypeService.get_all()
    return template_field_types


@router.get("/{id}", summary="Получить тип поля с заданным id")
async def get_template_field_type_by_id(
    id: idpk,
) -> Optional[TemplateFieldTypeReadDTO]:
    template_field_type = await TemplateFieldTypeService.get(id=id)
    return template_field_type


@router.put("/{id}", summary="Обновить тип с заданным id")
async def update_template_field_type(
    id: idpk, data: TemplateFieldTypeAddDTO
) -> Optional[TemplateFieldTypeReadDTO]:
    template_field_type = await TemplateFieldTypeService.update(id, data)
    return template_field_type


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить тип для полей шаблона",
)
async def add_template_field_type(
    data: TemplateFieldTypeAddDTO,
) -> Optional[TemplateFieldTypeReadDTO]:
    field_type = await TemplateFieldTypeService.add(data)
    return field_type


@router.post(
    "/list",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить список типов для полей шаблона",
)
async def add_template_field_type_list(
    data: list[TemplateFieldTypeAddDTO],
) -> Optional[list[TemplateFieldTypeReadDTO]]:
    field_types = await TemplateFieldTypeService.add_list(data)
    return field_types


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип",
)
async def delete_template(id: idpk):
    await TemplateFieldTypeService.delete(id)
