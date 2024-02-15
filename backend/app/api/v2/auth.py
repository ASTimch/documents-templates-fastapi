from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

view_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@view_router.get(
    "/login",
    summary="Авторизация",
)
async def view_auth_login(
    request: Request,
):
    return templates.TemplateResponse(
        "login.jinja",
        {
            "request": request,
        },
    )
