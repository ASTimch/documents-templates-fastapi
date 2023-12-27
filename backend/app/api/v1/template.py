import logging
from typing import Optional

from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from app.auth import (
    current_superuser,
    current_active_user,
    current_user_or_none,
)
from app.models.user import User
from app.schemas.template import (
    TemplateFieldReadDTO,
    TemplateFieldWriteValueListDTO,
    TemplateReadDTO,
    TemplateReadMinifiedDTO,
    TemplateWriteDTO,
)
from app.services.favorite import TemplateFavoriteService
from app.services.template import TemplateService

router = APIRouter()


@router.get("/", summary="Получить все доступные шаблоны")
async def get_all_templates(
    user: Optional[User] = Depends(current_user_or_none),
) -> Optional[list[TemplateReadMinifiedDTO]]:
    print("get_templates!!!")
    templates = await TemplateService.get_all(user=user)
    return templates


@router.get("/{template_id}", summary="Шаблон с заданным template_id")
async def get_template_by_id(
    template_id: int,
    user: Optional[User] = Depends(current_user_or_none),
) -> Optional[TemplateReadDTO]:
    template = await TemplateService.get(id=template_id, user=user)
    return template


@router.put("/{template_id}", summary="Обновить шаблон")
async def update_template(
    template_id: int, user: User = Depends(current_superuser)
):
    raise NotImplementedError


@router.patch(
    "/{template_id}/upload_template",
    summary="Обновить docx шаблон",
    status_code=status.HTTP_200_OK,
)
async def upload_docx_template(
    template_id: int, file: UploadFile, user: User = Depends(current_superuser)
):
    await TemplateService.update_docx_template(template_id, file)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, summary="Добавить шаблон"
)
async def add_template(
    data: TemplateWriteDTO, user: User = Depends(current_superuser)
) -> Optional[TemplateReadDTO]:
    template_id = await TemplateService.add(data)
    tempalte_dao = await TemplateService.get(id=template_id)
    return tempalte_dao


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить шаблон",
)
async def delete_template(
    template_id: int, user: User = Depends(current_superuser)
):
    await TemplateService.delete(template_id)


@router.get(
    "/{template_id}/check_consistency",
    summary="Проверить согласованность полей и тэгов docx шаблона",
    status_code=status.HTTP_200_OK,
)
async def check_consistency(
    template_id: int, user: User = Depends(current_superuser)
):
    result = await TemplateService.get_consistency_errors(template_id)
    return JSONResponse(content=result)


@router.get(
    "/{template_id}/download_draft",
    summary="Получить файл черновика в формате docx или pdf",
    status_code=status.HTTP_200_OK,
)
async def get_draft(template_id: int, pdf: bool = False) -> FileResponse:
    file, filename = await TemplateService.get_draft(template_id, pdf)
    response = await TemplateService.get_file_response(file, filename, pdf)
    return response


@router.post(
    "/{template_id}/download_preview",
    summary="Получить превью документа в формате docx или pdf",
    status_code=status.HTTP_200_OK,
)
async def get_preview(
    template_id: int,
    field_values: TemplateFieldWriteValueListDTO,
    pdf: bool = False,
) -> FileResponse:
    file, filename = await TemplateService.get_preview(
        template_id,
        field_values.model_dump()["fields"],
        pdf,
    )
    response = await TemplateService.get_file_response(file, filename, pdf)
    return response


@router.post(
    "/{template_id}/favorite/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить шаблон в избранное",
)
async def add_template_to_favorite(
    template_id: int,
    user: User = Depends(current_active_user),
) -> Optional[TemplateReadDTO]:
    template_dao = await TemplateService.get(id=template_id)
    await TemplateFavoriteService.add_favorite(
        user_id=user.id, template_id=template_dao.id
    )


@router.delete(
    "/{template_id}/favorite/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить шаблон из избранного",
)
async def delete_template(
    template_id: int, user: User = Depends(current_active_user)
):
    template_dao = await TemplateService.get(id=template_id)
    await TemplateFavoriteService.delete_favorite(
        user_id=user.id, template_id=template_dao.id
    )
