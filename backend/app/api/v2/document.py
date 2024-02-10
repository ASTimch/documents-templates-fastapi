from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.models.user import User
from app.schemas.document import (
    DocumentReadDTO,
    DocumentReadMinifiedDTO,
    DocumentWriteDTO,
    document_id_type,
)
from app.services.document import DocumentService

view_router = APIRouter()
from app.auth import current_active_user

templates = Jinja2Templates(directory="app/templates")


@view_router.get(
    "/{document_id}",
    summary="Получить документ с заданным document_id",
)
async def view_document_by_id(
    document_id: document_id_type,
    request: Request,
    user: Optional[User] = Depends(current_active_user),
):
    dto = await DocumentService.get(id=document_id, user=user)
    return templates.TemplateResponse(
        "document.jinja", {"request": request, "data": dto.model_dump()}
    )


@view_router.get("/", summary="Получить все документы пользователя")
async def view_get_all_documents(
    request: Request,
    user: User = Depends(current_active_user),
) -> Optional[list[DocumentReadMinifiedDTO]]:
    dto_list = await DocumentService.get_all(user=user) if user else []
    docs_list = [dto.model_dump() for dto in dto_list]
    print(dto_list)
    print(docs_list)
    return templates.TemplateResponse(
        "document_list.jinja", {"request": request, "data": docs_list}
    )
