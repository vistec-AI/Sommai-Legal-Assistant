import json
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app import crud, models, schemas
from app.api import deps
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/", response_model=List[schemas.InferenceModel])
def read_models(
  db: Session = Depends(deps.get_db),
  skip: int = 0,
  limit: int = 10000,
) -> Any:
  inference_models = crud.inference_model.list_all(db=db, skip=skip, limit=limit)

  inference_models.sort(key=lambda x: x.name, reverse=False)

  return inference_models

@router.post("/", response_model=schemas.InferenceModel)
def create_inference_model(
    *,
    db: Session = Depends(deps.get_db),
    inference_mode_in: schemas.InferenceModelCreate,
) -> Any:
    new_inference_model = crud.inference_model.create(
        db=db, obj_in=inference_mode_in
    )
    return new_inference_model

@router.put("/{id}", response_model=schemas.InferenceModel)
def update_inference_model(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    inference_mode_in: schemas.InferenceModelUpdate,
) -> Any:
    inference_model = crud.inference_model.get(db=db, id=id)
    if not inference_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference model not found"
            }
        )

    inference_model = crud.inference_model.update(db=db, db_obj=inference_model, obj_in=inference_mode_in)
    return inference_model

@router.delete("/{id}", response_model=schemas.InferenceModel)
def delete_inference_model(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    inference_model = crud.inference_model.get(db=db, id=id)
    if not inference_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "Inference model not found"
            }
        )
    inference_model = crud.inference_model.remove(db=db, id=id)
    return inference_model