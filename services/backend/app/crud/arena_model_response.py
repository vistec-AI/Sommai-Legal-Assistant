from typing import List
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.arena_model_response import ArenaModelResponse
from app.schemas.arena_model_response import ArenaModelResponseCreate, ArenaModelResponseUpdate

class CRUDTemplate(CRUDBase[ArenaModelResponse, ArenaModelResponseCreate, ArenaModelResponseUpdate]):
    def create(
        self, db: Session, *, obj_in: ArenaModelResponseCreate, user_id: UUID
    ) -> ArenaModelResponse:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_all(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[ArenaModelResponse]:
        return (
            db.query(self.model)
            .filter(ArenaModelResponse.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_arena_id(
        self, db: Session, *, user_id: UUID, arena_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[ArenaModelResponse]:
        return (
            db.query(self.model)
            .filter((ArenaModelResponse.arena_id == arena_id))
            .filter(ArenaModelResponse.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


arena_model_response = CRUDTemplate(ArenaModelResponse)
