"""
Modelo de Mensaje dentro de un ticket.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class MessageRole(str, enum.Enum):
    """Roles posibles de un mensaje."""
    USER = "user"          # Mensaje del usuario/cliente
    ASSISTANT = "assistant" # Mensaje del agente IA
    SYSTEM = "system"      # Mensaje del sistema (notificaciones, cambios de estado)


class Message(Base):
    """Modelo de mensaje dentro de un ticket."""
    
    __tablename__ = "messages"
    
    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, index=True)
    
    role = Column(SQLEnum(MessageRole), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Metadata adicional (fuentes RAG, tokens usados, etc.)
    meta_data = Column(JSONB, nullable=True, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    ticket = relationship("Ticket", back_populates="messages")
    
    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{preview}')>"
    
    def to_dict(self):
        """Convierte el mensaje a diccionario para el agente."""
        return {
            "role": self.role.value,
            "content": self.content,
            "metadata": self.meta_data or {}
        }