from app.db.base_class import Base, BaseMixin
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column


class InferenceModel(Base, BaseMixin):
    __tablename__ = "inference_model"

    name: Mapped[str] = mapped_column()
    domain: Mapped[str] = mapped_column()
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    llm_name: Mapped[str] = mapped_column(server_default="", nullable=True)

    def __repr__(self) -> str:
        return f"InferenceModel(id={self.id!r}"
