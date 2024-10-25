from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4


# Shared properties
class InferenceModelBase(BaseModel):
    pass


# Properties to receive via API on creation
class InferenceModelCreate(InferenceModelBase):
    name: str
    llm_name: str
    domain: str
    available: Optional[bool] = True

# Properties to receive via API on update
class InferenceModelUpdate(InferenceModelBase):
    name: Optional[str] = ""
    llm_name: Optional[str] = ""
    domain: Optional[str] = ""
    available: Optional[bool] = True

class InferenceModelInDBBase(InferenceModelBase):
    created_at: datetime
    id: UUID4
    name: str
    llm_name: str
    domain: str
    available: Optional[bool] = True
    updated_at: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
class InferenceModel(InferenceModelInDBBase):
    pass


# Additional properties stored in DB
class InferenceModelInDB(InferenceModelInDBBase):
    pass
