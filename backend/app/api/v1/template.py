from typing import Optional
from fastapi import APIRouter, status
from app.schemas.template import TemplateRead, TemplateReadMinified
from app.services.template import TemplateService

router = APIRouter()


@router.get("/", summary="Получить все доступные шаблоны")
async def get_all_templates() -> Optional[list[TemplateReadMinified]]:
    templates = await TemplateService.get_all()
    return templates


@router.get("/{template_id}", summary="Шаблон с заданным template_id")
async def get_template_by_id(template_id: int) -> Optional[TemplateRead]:
    template = await TemplateService.get(id=template_id)
    return template


@router.put("/{template_id}", summary="Обновить шаблон")
async def update_template(template_id: int):
    pass


@router.post(
    "/", status_code=status.HTTP_201_CREATED, summary="Добавить шаблон"
)
async def add_one_template():
    pass


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить шаблон",
)
async def delete_template(template_id: int):
    pass
