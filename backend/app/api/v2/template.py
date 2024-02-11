from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.auth import current_user_or_none
from app.models.user import User
from app.schemas.template import TemplateReadDTO, template_id_type
from app.services.template import TemplateService

view_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@view_router.get(
    "/{template_id}",
    summary="Получить шаблон с заданным template_id",
)
async def view_template_by_id(
    template_id: template_id_type,
    request: Request,
    user: Optional[User] = Depends(current_user_or_none),
):
    dto = await TemplateService.get(id=template_id, user=user)
    return templates.TemplateResponse(
        "template.jinja",
        {"request": request, "data": dto.model_dump(), "user": user},
    )


@view_router.get("/", summary="Получить все шаблоны")
async def view_get_all_templates(
    request: Request,
    user: Optional[User] = Depends(current_user_or_none),
) -> Optional[list[TemplateReadDTO]]:
    dto_list = await TemplateService.get_all(user=user)
    tpl_list = [dto.model_dump() for dto in dto_list]
    return templates.TemplateResponse(
        "template_list.jinja",
        {"request": request, "data": tpl_list, "user": user},
    )
