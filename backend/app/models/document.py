from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.template import Template, TemplateField
    from app.models.user import User


class DocumentField(Base):
    __tablename__ = "document_field"

    value: Mapped[Optional[str]] = mapped_column(Text)
    template_field_id: Mapped[int] = mapped_column(
        ForeignKey("template_field.id", ondelete="CASCADE")
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("document.id", ondelete="CASCADE")
    )

    document: Mapped["Document"] = relationship(back_populates="fields")
    template_field: Mapped["TemplateField"] = relationship(viewonly=True)

    def __str__(self):
        return f"{self.document_id}: {self.id}: {self.value}"


class Document(TimestampMixin, Base):
    __tablename__ = "document"

    description: Mapped[Optional[str]]
    template_id: Mapped[int] = mapped_column(
        ForeignKey("template.id", ondelete="CASCADE"), nullable=False
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    completed: Mapped[bool] = mapped_column(default=False)
    template: Mapped["Template"] = relationship("Template")
    owner: Mapped["User"] = relationship("User", back_populates="documents")
    fields: Mapped[list["DocumentField"]] = relationship(
        back_populates="document"
    )

    def __str__(self):
        return f"{self.id}: {self.description}"
