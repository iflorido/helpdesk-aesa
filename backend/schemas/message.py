"""
Schemas Pydantic para Messages (chat).
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

from db.models import MessageRole


class MessageBase(BaseModel):
    """Schema base para mensaje."""
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema para crear un mensaje."""
    pass


class MessageInDB(MessageBase):
    """Schema de mensaje en base de datos."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    ticket_id: UUID
    role: MessageRole
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class MessageResponse(MessageInDB):
    """Schema de respuesta pública de mensaje."""
    pass


class ChatHistoryResponse(BaseModel):
    """Schema para historial de chat de un ticket."""
    ticket_id: UUID
    messages: list[MessageResponse]
    total_messages: int