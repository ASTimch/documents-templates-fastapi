from typing import Optional

from fastapi import APIRouter, Depends, status

from app.auth import current_superuser
from app.database import idpk
from app.models.user import User
from app.schemas.template import (
    TemplateFieldTypeReadDTO,
    TemplateFieldTypeWriteDTO,
)
from app.services.template import TemplateFieldTypeService

router = APIRouter()


@router.get("/", summary="Получить все доступные типы полей")
async def get_all_template_field_types() -> (
    Optional[list[TemplateFieldTypeReadDTO]]
):
    return await TemplateFieldTypeService.get_all()


@router.get("/{id}", summary="Получить тип поля с заданным id")
async def get_template_field_type_by_id(
    id: idpk,
) -> Optional[TemplateFieldTypeReadDTO]:
    return await TemplateFieldTypeService.get(id=id)


@router.put("/{id}", summary="Обновить тип с заданным id")
async def update_template_field_type(
    id: idpk,
    data: TemplateFieldTypeWriteDTO,
    user: User = Depends(current_superuser),
) -> Optional[TemplateFieldTypeReadDTO]:
    return await TemplateFieldTypeService.update(id, data)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить тип для полей шаблона",
)
async def add_template_field_type(
    data: TemplateFieldTypeWriteDTO, user: User = Depends(current_superuser)
) -> Optional[TemplateFieldTypeReadDTO]:
    return await TemplateFieldTypeService.add(data)


@router.post(
    "/list",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить список типов для полей шаблона",
)
async def add_template_field_type_list(
    data: list[TemplateFieldTypeWriteDTO],
    user: User = Depends(current_superuser),
) -> Optional[list[TemplateFieldTypeReadDTO]]:
    return await TemplateFieldTypeService.add_list(data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип",
)
async def delete_template(id: idpk, user: User = Depends(current_superuser)):
    await TemplateFieldTypeService.delete(id)
