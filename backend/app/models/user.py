from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "user"

    email: Mapped[str]
    password: Mapped[str]

    templates: Mapped[list["Template"]] = relationship(
        "Template", back_populates="owner"
    )

    def __str__(self):
        return self.email
