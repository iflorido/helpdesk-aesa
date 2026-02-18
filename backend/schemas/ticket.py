"""
Schemas Pydantic para Tickets.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

from db.models import TicketStatus, TicketPriority, TicketCategory


class TicketBase(BaseModel):
    """Schema base para ticket."""
    title: str = Field(..., min_length=3, max_length=500)
    category: Optional[TicketCategory] = TicketCategory.GENERAL


class TicketCreate(TicketBase):
    """Schema para crear un ticket."""
    pass


class TicketUpdate(BaseModel):
    """Schema para actualizar un ticket."""
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None


class TicketInDB(TicketBase):
    """Schema de ticket en base de datos."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    escalated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TicketResponse(TicketInDB):
    """Schema de respuesta pública de ticket."""
    message_count: int = 0  # Será calculado


class TicketListResponse(BaseModel):
    """Schema para lista de tickets con paginación."""
    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int