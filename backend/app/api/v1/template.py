import logging
from typing import Optional
from fastapi import APIRouter, Response, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from app.schemas.template import (
    TemplateFieldReadDTO,
    TemplateReadDTO,
    TemplateReadMinifiedDTO,
    TemplateWriteDTO,
)
from app.services.template import TemplateService

router = APIRouter()


@router.get("/", summary="Получить все доступные шаблоны")
async def get_all_templates() -> Optional[list[TemplateReadMinifiedDTO]]:
    templates = await TemplateService.get_all()
    return templates


@router.get("/{template_id}", summary="Шаблон с заданным template_id")
async def get_template_by_id(template_id: int) -> Optional[TemplateReadDTO]:
    template = await TemplateService.get(id=template_id)
    return template


@router.put("/{template_id}", summary="Обновить шаблон")
async def update_template(template_id: int):
    pass


@router.patch(
    "/{template_id}/upload_template",
    summary="Обновить docx шаблон",
    status_code=status.HTTP_200_OK,
)
async def upload_docx_template(template_id: int, file: UploadFile):
    await TemplateService.update_docx_template(template_id, file)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, summary="Добавить шаблон"
)
async def add_template(data: TemplateWriteDTO) -> Optional[TemplateReadDTO]:
    template_id = await TemplateService.add(data)
    tempalte_dao = await TemplateService.get(id=template_id)
    return tempalte_dao


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить шаблон",
)
async def delete_template(template_id: int):
    await TemplateService.delete(template_id)


@router.get(
    "/{template_id}/check_consistency",
    summary="Проверить согласованность полей и тэгов docx шаблона",
    status_code=status.HTTP_200_OK,
)
async def check_consistency(template_id: int):
    result = await TemplateService.get_consistency_errors(template_id)
    return JSONResponse(content=result)


@router.get(
    "/{template_id}/download_draft",
    summary="Получить файл черновика в формате docx или pdf",
    status_code=status.HTTP_200_OK,
)
async def check_consistency(
    template_id: int, pdf: bool = False
) -> FileResponse:
    try:
        file, filename = await TemplateService.get_draft(template_id, pdf)
    except Exception:
        logging.exception("Pdf conversion failed")
        return Response("Pdf conversion failed", status_code=503)
    response = await TemplateService.get_file_response(file, filename, pdf)
    return response
