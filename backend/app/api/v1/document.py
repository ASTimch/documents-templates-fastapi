from typing import Optional

from fastapi import APIRouter, Depends, Response, UploadFile, status

from app.auth import (
    current_active_user,
    current_superuser,
    current_user_or_none,
)
from app.models.base import pk_type
from app.models.user import User
from app.schemas.document import (
    DocumentReadDTO,
    DocumentReadMinifiedDTO,
    DocumentWriteDTO,
)
from app.services.document import DocumentService

# from fastapi.responses import FileResponse, JSONResponse


router = APIRouter()


@router.get("/", summary="Получить все доступные документы")
async def get_all_documents(
    user: User = Depends(current_active_user),
) -> Optional[list[DocumentReadMinifiedDTO]]:
    if user:
        return await DocumentService.get_all(user=user)
    return None


@router.get(
    "/{document_id}",
    summary="Получить документ с заданным document_id",
)
async def get_document_by_id(
    document_id: pk_type,
    user: Optional[User] = Depends(current_active_user),
) -> Optional[DocumentReadDTO]:
    return await DocumentService.get(id=document_id, user=user)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить документ",
)
async def add_document(
    data: DocumentWriteDTO, user: User = Depends(current_active_user)
) -> Optional[DocumentReadDTO]:
    document_id = await DocumentService.add(data, user)
    document_dao = await DocumentService.get(id=document_id, user=user)
    return document_dao
