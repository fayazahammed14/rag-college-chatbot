from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

RoleType = Literal["student", "admin"]


class ProfileBase(BaseModel):
    name: Optional[str] = None
    role: RoleType = "student"


class ProfileResponse(ProfileBase):
    id: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[RoleType] = None
