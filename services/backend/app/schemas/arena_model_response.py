from pydantic import UUID4, BaseModel
from typing import Optional, List
from datetime import datetime
from app.custom_models.models import LawReference

class ArenaModelResponseBase(BaseModel):
  id: UUID4
  arena_id: UUID4
  inference_model_id: UUID4
  question: str
  answer: Optional[str] = None
  user_id: UUID4
  alias: str
  law_references: Optional[List[LawReference]] = None
  rating: Optional[str] = ""
  status: Optional[str] = ""
  created_at: datetime
  updated_at: datetime

  class Config:
      from_attributes = True

class ArenaModelResponseCreate(BaseModel):
  arena_id: UUID4
  inference_model_id: UUID4
  alias: str
  question: str
  status: Optional[str] = "PROCESSING"

class ArenaModelResponseUpdate(BaseModel):
  answer: Optional[str] = None
  rating: Optional[str] = ""
  status: Optional[str] = ""
  law_references: Optional[List[LawReference]] = None

class ArenaModelResponseInDBBase(ArenaModelResponseBase):
  id: UUID4
  alias: str
  question: str
  answer: Optional[str]
  arena_id: UUID4
  inference_model_id: UUID4
  user_id: UUID4
  law_references: Optional[List[LawReference]] = None
  rating: Optional[str]
  status: Optional[str] = ""
  created_at: datetime
  updated_at: datetime

  class Config:
      from_attributes = True

class ArenaModelResponse(ArenaModelResponseInDBBase):
  pass

class ArenaModelResponseInDB(ArenaModelResponseInDBBase):
    pass
