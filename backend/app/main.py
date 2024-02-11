from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.views import init_admin
from app.api import routers
from app.config import settings
from app.database import engine

app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    # lifespan=register_init,
)


app.include_router(routers.v1)
app.include_router(routers.v2)
app.mount(
    "/static", StaticFiles(directory="/docx_storage/tpl_thumbnails/"), "static"
)

# подключение админки
init_admin(app, engine)

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("app.main:app", reload=True)

# admin = Admin(app, engine, authentication_backend=authentication_backend)
# admin.add_view(UsersAdmin)
# admin.add_view(HotelsAdmin)
