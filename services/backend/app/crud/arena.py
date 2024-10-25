from typing import List
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.arena import Arena
from app.schemas.arena import ArenaCreate, ArenaUpdate, ArenaWithQuestion

class CRUDTemplate(CRUDBase[Arena, ArenaCreate, ArenaUpdate]):
    def create(
        self, db: Session, *, obj_in: ArenaCreate, user_id: UUID
    ) -> Arena:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_all(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[Arena]:
        return (
            db.query(self.model)
            .filter(Arena.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

arena = CRUDTemplate(Arena)
