from datetime import datetime
from pydantic import UUID4, BaseModel
from typing import List, Optional
from .arena_model_response import ArenaModelResponseBase

class ArenaBase(BaseModel):
    id: UUID4
    user_id: UUID4
    question: str
    created_at: datetime
    updated_at: datetime

    arena_model_responses: List[ArenaModelResponseBase] = []
    class Config:
        from_attributes = True

class ArenaCreate(BaseModel):
    question: str

class ArenaUpdate(BaseModel):
    pass

class ArenaInDBBase(ArenaBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    question: str

    class Config:
        from_attributes = True

class ArenaWithQuestion(BaseModel):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    question: str

    arena_model_responses: List[ArenaModelResponseBase] = []
    class Config:
        from_attributes = True

class Arena(ArenaInDBBase):
    pass

class ArenaInDB(ArenaInDBBase):
    pass
