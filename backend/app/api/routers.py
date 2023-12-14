from app.api.v1.template import router as template_router
from app.config import settings
from fastapi import APIRouter

v1 = APIRouter(prefix=settings.API_V1_PREFIX)
# v1 = APIRouter(prefix="api/v1")

# v1.include_router(auth_router, prefix='/auth', tags=['Авторизация])
# v1.include_router(user_router, prefix='/users', tags=['Пользователь'])
v1.include_router(template_router, prefix='/template', tags=['Шаблоны'])
