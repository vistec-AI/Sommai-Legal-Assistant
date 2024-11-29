from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4
from app.custom_models.models import UserStatus


# Shared properties
class UserBase(BaseModel):
   pass

class UserRequestCreate(UserBase):
    email: str
    password: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    keycloak_user_id: UUID4
    status: Optional[str] = "ACTIVE"
    has_accepted_terms: Optional[bool] = True
    token: Optional[str] = None
    token_expiration: Optional[datetime] = None

# Properties to receive via API on update
class UserUpdate(UserBase):
    status: Optional[str] = ""
    token: Optional[str] = None
    token_expiration: Optional[datetime] = None
    has_accepted_terms: Optional[bool] = False

class UserInDBBase(UserBase):
    id: UUID4
    keycloak_user_id: UUID4
    email: str
    status: Optional[str] = "ACTIVE"
    created_at: datetime
    updated_at: datetime
    token: Optional[str] = None
    token_expiration: Optional[datetime] = None
    has_accepted_terms: Optional[bool] = False

    class Config:
        from_attributes = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    pass
