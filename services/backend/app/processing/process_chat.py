from fastapi import Depends
from app.api import deps
from app.db.session import SessionLocal
from app import crud, schemas

class ChatProcessor:
  @staticmethod
  async def save_chat_history(chat_id: str, answer: str, status: str) -> None:
    db =  SessionLocal()
    chat_in = schemas.ChatUpdate(answer=answer, status=status)
    chat = crud.chat.get(db=db, id=chat_id)
    if chat:
      try:
        crud.chat.update(db=db, db_obj=chat, obj_in=chat_in)
      finally:
        db.close()
