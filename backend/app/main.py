from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import routers
from app.config import settings

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

app.mount("/static", StaticFiles(directory="app/static"), "static")

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("app.main:app", reload=True)
