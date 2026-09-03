from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationBase(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationCreate(ConversationBase):
    user_id: Optional[str] = None


class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageInConversation(BaseModel):
    id: str
    role: str
    content: str
    sources: List[dict] = []
    created_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageInConversation] = []
