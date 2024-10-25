from app.db.base_class import Base, BaseMixin
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import UUID4
from sqlalchemy import Boolean
from datetime import datetime


class User(Base, BaseMixin):
    # __tablename__ generated by Base

    email: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(server_default="", nullable=True)
    keycloak_user_id: Mapped[UUID4] = mapped_column()
    token: Mapped[str] = mapped_column(server_default=None, nullable=True)
    token_expiration: Mapped[datetime] = mapped_column(server_default=None, nullable=True)
    has_accepted_terms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}"
