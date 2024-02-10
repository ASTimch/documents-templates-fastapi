from typing import Optional

from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from app.auth import (
    current_active_user,
    current_superuser,
    current_user_or_none,
)
from app.common.utils import get_file_response
from app.config import settings
from app.models.user import User
from app.schemas.template import (
    TemplateFieldWriteValueListDTO,
    TemplateReadDTO,
    TemplateReadMinifiedDTO,
    TemplateWriteDTO,
)
from app.services.favorite import TemplateFavoriteService
from app.services.pdf_converter import PdfConverter
from app.services.template import TemplateService
from app.tasks.tasks import generate_template_thumbnail

router = APIRouter()


@router.get("/", summary="Получить все доступные шаблоны")
async def get_all_templates(
    user: Optional[User] = Depends(current_user_or_none),
) -> Optional[list[TemplateReadMinifiedDTO]]:
    templates = await TemplateService.get_all(user=user)
    return templates


@router.get("/{template_id}", summary="Получить шаблон с заданным template_id")
async def get_template_by_id(
    template_id: int,
    user: Optional[User] = Depends(current_user_or_none),
) -> Optional[TemplateReadDTO]:
    template = await TemplateService.get(id=template_id, user=user)
    return template


# @router.put("/{template_id}", summary="Обновить шаблон")
# async def update_template(
#     template_id: int, user: User = Depends(current_superuser)
# ):
#     raise NotImplementedError


@router.patch(
    "/{template_id}/upload_template",
    summary="Обновить docx шаблон",
    status_code=status.HTTP_200_OK,
)
async def upload_docx_template(
    template_id: int, file: UploadFile, user: User = Depends(current_superuser)
):
    await TemplateService.update_docx_template(template_id, file)
    # Запуск фоновой задачи для генерации новой картинки thumbnail
    generate_template_thumbnail.delay(template_id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, summary="Добавить шаблон"
)
async def add_template(
    data: TemplateWriteDTO, user: User = Depends(current_superuser)
) -> Optional[TemplateReadDTO]:
    template_id = await TemplateService.add(data)
    template_dao = await TemplateService.get(id=template_id)
    return template_dao


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
async def download_draft(template_id: int, pdf: bool = False) -> FileResponse:
    file, filename = await TemplateService.get_draft(template_id, pdf)
    response = await get_file_response(file, filename, pdf)
    return response


@router.get(
    "/{template_id}/get_thumbnail",
    summary="Сгенерировать и скачать миниатюру.",
    status_code=status.HTTP_200_OK,
)
async def get_thumbnail(template_id: int) -> FileResponse:
    pdf_buffer, _ = await TemplateService.get_draft(template_id, pdf=True)
    png_buffer = PdfConverter.pdf_to_thumbnail(
        pdf_buffer,
        settings.THUMBNAIL_WIDTH,
        settings.THUMBNAIL_HEIGHT,
        settings.THUMBNAIL_FORMAT,
    )
    response = Response(content=png_buffer.getvalue(), media_type="image/png")
    return response


@router.get(
    "/{template_id}/generate_thumbnail",
    summary="Сгенерировать миниатюру.",
    status_code=status.HTTP_200_OK,
)
async def generate_thumbnail(template_id: int):
    await TemplateService.generate_thumbnail(template_id)


@router.post(
    "/{template_id}/download_preview",
    summary="Получить превью документа в формате docx или pdf",
    status_code=status.HTTP_200_OK,
)
async def download_preview(
    template_id: int,
    field_values: TemplateFieldWriteValueListDTO,
    pdf: bool = False,
) -> FileResponse:
    file, filename = await TemplateService.get_preview(
        template_id,
        field_values.model_dump()["fields"],
        pdf,
    )
    response = await get_file_response(file, filename, pdf)
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
async def delete_template_from_favorite(
    template_id: int, user: User = Depends(current_active_user)
):
    template_dao = await TemplateService.get(id=template_id)
    await TemplateFavoriteService.delete_favorite(
        user_id=user.id, template_id=template_dao.id
    )
