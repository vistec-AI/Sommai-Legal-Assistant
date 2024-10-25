from typing import List
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.inference_model import InferenceModel
from app.schemas.inference_model import InferenceModelCreate, InferenceModelUpdate

class CRUDTemplate(CRUDBase[InferenceModel, InferenceModelCreate, InferenceModelUpdate]):
    def create(
        self, db: Session, *, obj_in: InferenceModelCreate
    ) -> InferenceModel:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_all(
        self, db: Session, *, skip: int = 0, limit: int = 10000
    ) -> List[InferenceModel]:
        return (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_inference_model_id(
        self, db: Session, *, inference_model_id: UUID, skip: int = 0, limit: int = 10000
    ) -> List[InferenceModel]:
        return (
            db.query(self.model)
            .filter((InferenceModel.id == inference_model_id))
            .offset(skip)
            .limit(limit)
            .all()
        )


inference_model = CRUDTemplate(InferenceModel)
