from fastapi import APIRouter

from app.auth import auth_backend, fastapi_users
from app.schemas.auth import UserCreate, UserRead

router = APIRouter()

router.include_router(
    # for verification
    # fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    fastapi_users.get_auth_router(auth_backend),
    prefix="",
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="",
)

# router.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )
