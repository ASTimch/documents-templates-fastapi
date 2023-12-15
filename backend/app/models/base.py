from datetime import datetime
from typing import Annotated
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    MappedAsDataclass,
)


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
