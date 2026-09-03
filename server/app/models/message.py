from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

RoleType = Literal["user", "assistant"]


class MessageSource(BaseModel):
    document_id: str
    document_title: str
    page_number: int
    similarity: Optional[float] = None


class MessageBase(BaseModel):
    conversation_id: str
    role: RoleType
    content: str
    sources: List[MessageSource] = []


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AskQuestionRequest(BaseModel):
    conversationId: Optional[str] = Field(None, description="Optional ID of existing conversation")
    question: str = Field(..., min_length=1, description="Student's query")


class AskQuestionResponse(BaseModel):
    answer: str
    sources: List[MessageSource] = []
    conversationId: str
