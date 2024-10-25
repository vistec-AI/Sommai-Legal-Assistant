import json
import os
from typing import Any, List, Optional
from uuid import UUID
import uuid
from app import crud, models, schemas
from app.api import deps
from app.api.custom_route import AuthenticatedRoute

import httpx

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

router = APIRouter(route_class=AuthenticatedRoute)

@router.get("/", response_model=List[schemas.ChatRoom])
def read_chat_rooms(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    skip: int = 0,
    limit: int = 10000,
) -> Any:
    chat_rooms = crud.chat_room.list_all(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

    chat_rooms.sort(key=lambda x: x.created_at, reverse=True)

    return chat_rooms

@router.get("/latest", response_model=schemas.ChatRoom)
def read_latest_chat_rooms(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    skip: int = 0,
    limit: int = 10000,
) -> Any:
    chat_rooms = crud.chat_room.list_latest(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

    return chat_rooms

@router.get("/{id}", response_model=schemas.ChatRoom)
def read_chat_room_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID
) -> Any:
    chat_room = crud.chat_room.get(db=db, id=id)
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat room not found"
            }
        )
    return chat_room

@router.post("/", response_model=schemas.ChatRoom)
def create_chat_room(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    chat_room_in: schemas.ChatRoomCreate,
) -> Any:
    new_chat_room = crud.chat_room.create(
        db=db, obj_in=chat_room_in, user_id=current_user.id
    )
    return new_chat_room


@router.put("/{id}", response_model=schemas.ChatRoom)
def update_chat_room(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    chat_room_in: schemas.ChatRoomUpdate,
) -> Any:
    chat_room = crud.chat_room.get(db=db, id=id)
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat room not found"
            }
        )

    chat_room = crud.chat_room.update(db=db, db_obj=chat_room, obj_in=chat_room_in)
    return chat_room

@router.delete("/{id}", response_model=schemas.ChatRoom)
def delete_chat_room(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    chat_room = crud.chat_room.get(db=db, id=id)
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Chat room not found"
            }
        )
    chat_room = crud.chat_room.remove(db=db, id=id)
    return chat_room