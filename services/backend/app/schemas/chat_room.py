from datetime import datetime
from pydantic import UUID4, BaseModel
from typing import List
from .chat import ChatBase

class ChatRoomBase(BaseModel):
    id: UUID4
    name: str
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    chats: List[ChatBase] = []
    class Config:
        from_attributes = True

class ChatRoomCreate(BaseModel):
    name: str

class ChatRoomUpdate(BaseModel):
    name: str

class ChatRoomInDBBase(ChatRoomBase):
    id: UUID4
    name: str
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRoom(ChatRoomInDBBase):
    pass

class ChatRoomInDB(ChatRoomInDBBase):
    pass
