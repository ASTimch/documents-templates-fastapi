from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.document import router as document_router
from app.api.v1.template import router as template_router
from app.api.v1.template_field_type import router as template_field_type_router
from app.api.v2.document import view_router as document_view_router
from app.config import settings

v1 = APIRouter(prefix=settings.API_V1_PREFIX)
# v1 = APIRouter(prefix="api/v1")

# v1.include_router(user_router, prefix='/users', tags=['Пользователь'])
v1.include_router(template_router, prefix="/template", tags=["Шаблоны"])
v1.include_router(document_router, prefix="/document", tags=["Документы"])
v1.include_router(
    template_field_type_router,
    prefix="/template_field_type",
    tags=["Типы полей шаблонов"],
)

v1.include_router(
    auth_router,
    prefix="/auth",
    tags=["Авторизация"],
)

v2 = APIRouter(prefix=settings.API_V2_PREFIX)
v2.include_router(document_view_router, prefix="/document", tags=["Документы"])
