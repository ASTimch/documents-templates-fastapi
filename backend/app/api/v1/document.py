from typing import Optional

from fastapi import APIRouter, Depends, Response, UploadFile, status

from app.auth import (
    current_active_user,
    current_superuser,
    current_user_or_none,
)
from app.models.user import User
from app.schemas.document import DocumentReadMinifiedDTO
from app.services.document import DocumentService

# from fastapi.responses import FileResponse, JSONResponse


router = APIRouter()


@router.get("/", summary="Получить все доступные документы")
async def get_all_templates(
    user: User = Depends(current_active_user),
) -> Optional[list[DocumentReadMinifiedDTO]]:
    if user:
        return await DocumentService.get_all(user=user)
    return None
