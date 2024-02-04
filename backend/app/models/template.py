from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    FileType,
    ImageType,
    TimestampMixin,
    pk_type,
    storage_docx,
    storage_thumbnail,
    str_50,
    str_256,
)

# from app.models.favorite import UserTemplateFavorite

# from fastapi_storages.integrations.sqlalchemy import FileType, ImageType
if TYPE_CHECKING:
    from app.models.user import User

from app.models.favorite import UserTemplateFavorite


class Category(Base):
    """Категория шаблонов"""

    __tablename__ = "category"

    name: Mapped[str]

    templates: Mapped[Optional[list["Template"]]] = relationship(
        back_populates="category"
    )

    def __str__(self):
        return f"{self.id}: {self.name}"


class TemplateFieldType(Base):
    """Тип полей шаблонов."""

    __tablename__ = "field_type"

    type: Mapped[str_50] = mapped_column(unique=True)
    name: Mapped[str_50]
    mask: Mapped[str_256] = mapped_column(nullable=True)

    def __str__(self):
        return f"{self.type} ({self.name})"


class TemplateFieldGroup(Base):
    """Группы полей шаблона."""

    __tablename__ = "field_group"

    template_id: Mapped[pk_type] = mapped_column(
        ForeignKey("template.id", ondelete="CASCADE")
    )
    name: Mapped[str]

    template: Mapped["Template"] = relationship(back_populates="groups")
    fields: Mapped[Optional[list["TemplateField"]]] = relationship(
        back_populates="group"
    )

    def __str__(self):
        return f"{self.template_id}: {self.id}: {self.name}"


class TemplateField(Base):
    """Поля шаблона."""

    __tablename__ = "template_field"

    tag: Mapped[str]
    name: Mapped[str]
    hint: Mapped[str] = mapped_column(nullable=True)
    default: Mapped[str] = mapped_column(nullable=True)
    length: Mapped[int] = mapped_column(
        default=100
    )  # only positive ?, default = 100

    template_id: Mapped[pk_type] = mapped_column(
        ForeignKey("template.id", ondelete="CASCADE")
    )
    group_id: Mapped[pk_type] = mapped_column(
        ForeignKey("field_group.id", ondelete="SET NULL"), nullable=True
    )
    type_id: Mapped[pk_type] = mapped_column(
        ForeignKey("field_type.id", ondelete="RESTRICT")
    )

    type: Mapped[Optional["TemplateFieldType"]] = relationship()
    group: Mapped[Optional["TemplateFieldGroup"]] = relationship(
        back_populates="fields"
    )
    template: Mapped["Template"] = relationship(back_populates="fields")

    def __str__(self):
        return f"{self.template_id}: {self.id}: {self.name}"

    # """Запрет назначения группы, привязанной к другому шаблону."""
    # if self.group and self.group.template != self.template:
    # raise ValidationError(Messages.WRONG_FIELD_AND_GROUP_TEMPLATES)


class Template(TimestampMixin, Base):
    """Шаблон."""

    __tablename__ = "template"

    owner_id: Mapped[Optional[pk_type]] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    category_id: Mapped[Optional[pk_type]] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"),
        nullable=True,
    )
    filename = mapped_column(FileType(storage=storage_docx), nullable=True)
    title: Mapped[str]
    description: Mapped[str]
    deleted: Mapped[bool] = mapped_column(default=False)
    thumbnail = mapped_column(
        ImageType(storage=storage_thumbnail), nullable=True
    )

    owner: Mapped["User"] = relationship(back_populates="templates")
    category: Mapped["Category"] = relationship(back_populates="templates")
    groups: Mapped[Optional[list["TemplateFieldGroup"]]] = relationship(
        back_populates="template", order_by=TemplateFieldGroup.id
    )
    fields: Mapped[Optional[list["TemplateField"]]] = relationship(
        back_populates="template", order_by=TemplateField.id
    )

    favorited_by_users: Mapped[list["User"]] = relationship(
        back_populates="favorite_templates",
        # secondary="user_template_favorite"
        secondary=UserTemplateFavorite.__table__,
    )

    def __str__(self):
        return f"{self.id}: {self.title}"
