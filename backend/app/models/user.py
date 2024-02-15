from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.document import Document

if TYPE_CHECKING:
    from app.models.template import Template

from app.models.favorite import UserTemplateFavorite


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    templates: Mapped[list["Template"]] = relationship(
        "Template", back_populates="owner"
    )
    favorite_templates: Mapped[list["Template"]] = relationship(
        back_populates="favorited_by_users",
        # secondary="user_template_favorite",
        secondary=UserTemplateFavorite.__table__,
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="owner"
    )

    def __str__(self):
        return self.email
