from datetime import datetime
from typing import Annotated, Any
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    MappedAsDataclass,
)
from fastapi_storages.integrations.sqlalchemy import FileType as _FileType
from fastapi_storages.integrations.sqlalchemy import ImageType as _ImageType
from fastapi_storages import FileSystemStorage
from app.config import settings

storage_docx = FileSystemStorage(path=settings.TEMPLATE_DOCX_DIR)
storage_thumbnail = FileSystemStorage(path=settings.TEMPLATE_THUMBNAIL_DIR)


class FileType(_FileType):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ImageType(_ImageType):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


str_50 = Annotated[str, 50]
str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    __abstract__ = True

    type_annotation_map = {str_50: String(50), str_256: String(256)}
    id: Mapped[int] = mapped_column(primary_key=True)

    def to_dict(self):
        return {
            field.name: getattr(self, field.name) for field in self.__table__.c
        }

    # @declared_attr.directive
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()


# class DateTimeMixin(MappedAsDataclass):

#     created_at: Mapped[datetime] = mapped_column(
#         init=False, default_factory=datetime.utcnow
#     )
#     updated_at: Mapped[datetime | None] = mapped_column(
#         init=False, onupdate=datetime.utcnow
#     )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        # server_default=func.now(),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        # server_default=func.now(),
        default=datetime.utcnow,
        # onupdate=func.now(),
    )
