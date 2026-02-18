"""
Modelo de Ticket (conversación/incidencia).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class TicketStatus(str, enum.Enum):
    """Estados posibles de un ticket."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    """Prioridades de un ticket."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    """Categorías de tickets."""
    TECHNICAL = "technical"
    LICENSING = "licensing"
    GENERAL = "general"
    DOCUMENTATION = "documentation"


class Ticket(Base):
    """Modelo de ticket/conversación."""
    
    __tablename__ = "tickets"
    
    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False, index=True)
    category = Column(SQLEnum(TicketCategory), default=TicketCategory.GENERAL, nullable=False, index=True)
    
    # Timestamps especiales
    escalated_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Timestamps estándar
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, status={self.status}, priority={self.priority})>"
    
    @property
    def is_open(self) -> bool:
        """Verifica si el ticket está abierto."""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
    
    @property
    def message_count(self) -> int:
        """Retorna el número de mensajes en el ticket."""
        return len(self.messages) if self.messages else 0