from typing import List
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.chat import Chat
from app.schemas.chat import ChatCreate, ChatUpdate

class CRUDTemplate(CRUDBase[Chat, ChatCreate, ChatUpdate]):
    def create(
        self, db: Session, *, obj_in: ChatCreate, user_id: UUID
    ) -> Chat:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_all(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[Chat]:
        return (
            db.query(self.model)
            .filter(Chat.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_chat_room_id(
        self, db: Session, *, user_id: UUID, chat_room_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[Chat]:
        return (
            db.query(self.model)
            .filter((Chat.chat_room_id == chat_room_id))
            .filter(Chat.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


chat = CRUDTemplate(Chat)
