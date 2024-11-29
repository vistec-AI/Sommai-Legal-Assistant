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

class UsedUserModel(BaseModel):
  email: str
  date: str

date_format = '%Y-%m-%d %H:%M:%S'

@router.get("/chats")
def listing_user(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,
    email: Optional[str] = Query(None, description="Filter by email"),
) -> Any:
    filtered_chats = db.query(Chat).all()

    responses = []
    for chat in filtered_chats:
        user = db.query(User).filter(User.id == chat.user_id).first()
        if user:
            responses.append(
                UsedUserModel(
                    email=user.email,
                    date=chat.created_at.strftime(date_format)
                )
            )
    if email:
      responses = [response for response in responses if response.email == email]
    email_map = {}
    for entry in responses:
        email = entry.email
        # Update the map to keep the latest date and total count
        if email in email_map:
            email_map[email]["latest_used_date"] = entry.date
            email_map[email]["total_chat"] += 1
        else:
            email_map[email] = {
                "email": entry.email,
                "latest_used_date": entry.date,
                "total_chat": 1
            }
    final_result = list(email_map.values())
    sorted_result = sorted(final_result, key=lambda x: datetime.strptime(x['latest_used_date'], date_format))

    return sorted_result


@router.get("/arena")
def listing_user(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,
    email: Optional[str] = Query(None, description="Filter by email"),
) -> Any:
    filtered_arena = db.query(Arena).all()

    responses = []
    for arena in filtered_arena:
        user = db.query(User).filter(User.id == arena.user_id).first()
        if user:
            responses.append(
                UsedUserModel(
                    email=user.email,
                    date=arena.created_at.strftime(date_format)
                )
            )
    if email:
      responses = [response for response in responses if response.email == email]
    email_map = {}
    for entry in responses:
        email = entry.email
        # Update the map to keep the latest date and total count
        if email in email_map:
            email_map[email]["latest_used_date"] = entry.date
            email_map[email]["total_arena"] += 1
        else:
            email_map[email] = {
                "email": entry.email,
                "latest_used_date": entry.date,
                "total_arena": 1
            }
    final_result = list(email_map.values())
    sorted_result = sorted(final_result, key=lambda x: datetime.strptime(x['latest_used_date'], date_format))

    return sorted_result
