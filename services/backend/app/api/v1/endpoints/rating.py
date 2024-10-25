from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, UUID4
from typing import List, Optional, Any
from app.api import deps
from app.models.chat import Chat
from app.models.user import User
from app.models.arena_model_response import ArenaModelResponse
from app.models.arena import Arena
from app.schemas.arena_model_response import ArenaModelResponseBase
from sqlalchemy.orm import Session
from sqlalchemy import and_
from enum import Enum
from datetime import datetime

router = APIRouter()

class MappedChatWithUserInfo(BaseModel):
  chat_id: UUID4
  user_id: UUID4
  question: str
  answer: str
  email: str
  rating: str
  feedback: str
  status: str

class MappedArenaWithUserInfo(BaseModel):
  arena_id: UUID4
  user_id: UUID4
  question: str
  arena_model_responses: List[ArenaModelResponseBase]
  email: str

class UsedUserModel(BaseModel):
  email: str
  date: str

from enum import Enum

class Rating(Enum):
    LIKE = "Like"
    DISLIKE = "Dislike"

@router.get("/chats", response_model=List[MappedChatWithUserInfo])
def rating_chats(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,
    rating: Optional[str] = Query(None, description="Filter by rating"),
    email: Optional[str] = Query(None, description="Filter by email"),
) -> Any:
    filtered_chats = db.query(Chat).filter(and_(
        Chat.rating != "",
        Chat.rating != None
    ))
    if rating is not None:
        try:
            Rating(rating)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "invalid_rating",
                    "description": f"Invalid status value. Allowed values are: {', '.join([e.value for e in Rating])}"
                }
            )
    if rating:
      filtered_chats = filtered_chats.filter(Chat.rating == rating)

    responses = []
    for chat in filtered_chats:
        user = db.query(User).filter(User.id == chat.user_id).first()
        if user:
            responses.append(
                MappedChatWithUserInfo(
                    chat_id=chat.id,
                    question=chat.question,
                    answer=chat.answer,
                    rating=chat.rating,
                    feedback=chat.feedback,
                    status=chat.status,
                    user_id=user.id,
                    email=user.email,
                )
            )
    if email:
      responses = [response for response in responses if response.email == email]
    return responses

@router.get("/arena", response_model=List[MappedArenaWithUserInfo])
def rating_arena(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,
    email: Optional[str] = Query(None, description="Filter by email"),
) -> Any:

    all_arena = db.query(Arena).all()
    filtered_arena = [
        arena for arena in all_arena
        if any(response.rating and isinstance(response.rating, str) for response in arena.arena_model_responses)
    ]
    responses = []
    for arena in filtered_arena:
        user = db.query(User).filter(User.id == arena.user_id).first()
        if user:
            responses.append(
                MappedArenaWithUserInfo(
                    arena_id=arena.id,
                    question=arena.question,
                    user_id=user.id,
                    email=user.email,
                    arena_model_responses=arena.arena_model_responses
                )
            )
    if email:
      responses = [response for response in responses if response.email == email]
    return responses