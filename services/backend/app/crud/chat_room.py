from typing import List
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.chat_room import ChatRoom
from app.schemas.chat_room import ChatRoomCreate, ChatRoomUpdate

class CRUDTemplate(CRUDBase[ChatRoom, ChatRoomCreate, ChatRoomUpdate]):
    def create(
        self, db: Session, *, obj_in: ChatRoomCreate, user_id: UUID
    ) -> ChatRoom:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_all(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[ChatRoom]:
        return (
            db.query(self.model)
            .filter(ChatRoom.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    def list_latest(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ChatRoom]:
        return (
            db.query(self.model)
            .filter(ChatRoom.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .first()
        )


chat_room = CRUDTemplate(ChatRoom)
