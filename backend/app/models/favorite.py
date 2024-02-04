# from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, pk_type

# if TYPE_CHECKING:
#     from app.models.template import Template
#     from app.models.user import User


class UserTemplateFavorite(Base):
    __tablename__ = "user_template_favorite"

    id: Mapped[pk_type] = mapped_column(
        primary_key=True,
        autoincrement=True,
        server_default=Identity(start=1, cycle=True),
    )

    user_id: Mapped[pk_type] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    template_id: Mapped[pk_type] = mapped_column(
        ForeignKey("template.id", ondelete="CASCADE"), primary_key=True
    )
