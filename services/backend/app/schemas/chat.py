from pydantic import UUID4, BaseModel
from typing import Optional, List
from datetime import datetime
from app.custom_models.models import LawReference

class ChatBase(BaseModel):
  id: UUID4
  question: str
  answer: Optional[str] = None
  chat_room_id: UUID4
  user_id: UUID4
  inference_model_id: UUID4
  law_references: Optional[List[LawReference]] = None
  rating: Optional[str] = ""
  status: Optional[str] = ""
  feedback: Optional[str] = ""
  created_at: datetime
  updated_at: datetime

  class Config:
      from_attributes = True

class ChatCreate(BaseModel):
  chat_room_id: UUID4
  inference_model_id: UUID4
  question: str
  status: Optional[str] = "PROCESSING"

class ChatUpdate(BaseModel):
  answer: Optional[str] = None
  rating: Optional[str] = ""
  status: Optional[str] = ""
  feedback: Optional[str] = ""
  law_references: Optional[List[LawReference]] = None

class ChatInDBBase(ChatBase):
  id: UUID4
  question: str
  answer: Optional[str]
  chat_room_id: UUID4
  inference_model_id: UUID4
  user_id: UUID4
  law_references: Optional[List[LawReference]] = None
  rating: Optional[str]
  feedback: Optional[str]
  status: Optional[str] = ""
  created_at: datetime
  updated_at: datetime

  class Config:
      from_attributes = True

class Chat(ChatInDBBase):
  pass

class ChatInDB(ChatInDBBase):
    pass
