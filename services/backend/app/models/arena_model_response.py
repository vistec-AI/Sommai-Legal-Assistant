from app.db.base_class import Base, BaseMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Uuid, JSON


class ArenaModelResponse(Base, BaseMixin):
    __tablename__ = "arena_model_response"

    arena_id: Mapped[Uuid] = mapped_column(ForeignKey("arena.id"))
    user_id: Mapped[Uuid] = mapped_column(ForeignKey("user.id"))
    inference_model_id: Mapped[Uuid] = mapped_column(ForeignKey("inference_model.id"))
    alias: Mapped[str] = mapped_column()
    question: Mapped[str] = mapped_column()
    answer: Mapped[str] = mapped_column(server_default="", nullable=True)
    status: Mapped[str] = mapped_column(server_default="")
    rating: Mapped[str] = mapped_column(server_default="", nullable=True)
    law_references: Mapped[JSON] = mapped_column(JSON, nullable=True)

    arena: Mapped["Arena"] = relationship(back_populates="arena_model_responses")

    def __repr__(self) -> str:
        return f"ArenaModelResponse(id={self.id!r}"
