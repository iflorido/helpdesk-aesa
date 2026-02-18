"""
Repositorio para operaciones de Message en la base de datos.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from db.models import Message, MessageRole


class MessageRepository:
    """Repositorio para gestionar mensajes."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Obtiene un mensaje por su ID."""
        return self.db.query(Message).filter(Message.id == message_id).first()
    
    def create(
        self,
        ticket_id: UUID,
        role: MessageRole,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """
        Crea un nuevo mensaje.
        
        Args:
            ticket_id: ID del ticket
            role: Rol del mensaje (user, assistant, system)
            content: Contenido del mensaje
            metadata: Metadata adicional (opcional)
        
        Returns:
            Message creado
        """
        message = Message(
            ticket_id=ticket_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def create_user_message(self, ticket_id: UUID, content: str) -> Message:
        """Crea un mensaje del usuario."""
        return self.create(ticket_id, MessageRole.USER, content)
    
    def create_assistant_message(
        self,
        ticket_id: UUID,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """Crea un mensaje del asistente con metadata opcional."""
        return self.create(ticket_id, MessageRole.ASSISTANT, content, metadata)
    
    def create_system_message(self, ticket_id: UUID, content: str) -> Message:
        """Crea un mensaje del sistema."""
        return self.create(ticket_id, MessageRole.SYSTEM, content)
    
    def list_by_ticket(
        self,
        ticket_id: UUID,
        skip: int = 0,
        limit: int = 1000
    ) -> list[Message]:
        """
        Lista todos los mensajes de un ticket ordenados cronológicamente.
        
        Args:
            ticket_id: ID del ticket
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
        """
        return (
            self.db.query(Message)
            .filter(Message.ticket_id == ticket_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_by_ticket(self, ticket_id: UUID) -> int:
        """Cuenta los mensajes de un ticket."""
        return self.db.query(Message).filter(Message.ticket_id == ticket_id).count()
    
    def get_conversation_history(
        self,
        ticket_id: UUID,
        limit: Optional[int] = None
    ) -> list[dict]:
        """
        Obtiene el historial de conversación en formato para el agente.
        
        Args:
            ticket_id: ID del ticket
            limit: Limitar a los últimos N mensajes (opcional)
        
        Returns:
            Lista de mensajes en formato {"role": "user|assistant", "content": "..."}
        """
        query = (
            self.db.query(Message)
            .filter(Message.ticket_id == ticket_id)
            .filter(Message.role.in_([MessageRole.USER, MessageRole.ASSISTANT]))
            .order_by(Message.created_at.asc())
        )
        
        if limit:
            query = query.limit(limit)
        
        messages = query.all()
        
        return [msg.to_dict() for msg in messages]