import json
import os
from typing import Any, List, Optional
from uuid import UUID
from pydantic import UUID4
import uuid
from app import crud, models, schemas
from app.api import deps
from app.api.custom_route import AuthenticatedRoute

import httpx

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

router = APIRouter(route_class=AuthenticatedRoute)

@router.get("/", response_model=List[schemas.Arena])
def read_arena_list(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    skip: int = 0,
    limit: int = 10000,
) -> Any:
    arena_list = crud.arena.list_all(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

    arena_list.sort(key=lambda x: x.created_at, reverse=True)

    return arena_list

@router.post("/", response_model=schemas.Arena)
def create_arena(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_user_by_token),
    arena_in: schemas.ArenaCreate,
) -> Any:
    new_arena = crud.arena.create(
        db=db, obj_in=arena_in,  user_id=current_user.id
    )
    return new_arena


@router.put("/{id}", response_model=schemas.Arena)
def update_arena(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    arena_in: schemas.ArenaUpdate,
) -> Any:
    arena = crud.arena.get(db=db, id=id)
    if not arena:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Arena not found"
            }
        )

    arena = crud.arena.update(db=db, db_obj=arena, obj_in=arena_in)
    return arena

@router.delete("/{id}", response_model=schemas.Arena)
def delete_arena(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    arena = crud.arena.get(db=db, id=id)
    if not arena:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Arena not found"
            }
        )
    arena = crud.arena.remove(db=db, id=id)
    return arena