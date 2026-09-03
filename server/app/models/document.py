from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

DocumentStatus = Literal["processing", "ready", "failed"]


class DocumentBase(BaseModel):
    title: str
    filename: str


class DocumentCreate(DocumentBase):
    uploaded_by: Optional[str] = None
    page_count: int = 0
    status: DocumentStatus = "processing"


class DocumentUpdate(BaseModel):
    title: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: str
    uploaded_by: Optional[str] = None
    status: DocumentStatus
    page_count: int
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    id: str
    title: str
    status: DocumentStatus
    page_count: int
    updated_at: datetime
