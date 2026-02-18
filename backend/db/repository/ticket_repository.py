"""
Repositorio para operaciones de Ticket en la base de datos.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from db.models import Ticket, TicketStatus, TicketPriority, TicketCategory


class TicketRepository:
    """Repositorio para gestionar tickets."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, ticket_id: UUID) -> Optional[Ticket]:
        """Obtiene un ticket por su ID."""
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    def create(
        self,
        user_id: UUID,
        title: str,
        category: TicketCategory = TicketCategory.GENERAL
    ) -> Ticket:
        """
        Crea un nuevo ticket.
        
        Returns:
            Ticket creado
        """
        ticket = Ticket(
            user_id=user_id,
            title=title,
            category=category,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
        )
        
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket
    
    def update(
        self,
        ticket_id: UUID,
        title: Optional[str] = None,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None,
    ) -> Optional[Ticket]:
        """
        Actualiza un ticket.
        
        Returns:
            Ticket actualizado o None si no existe.
        """
        ticket = self.get_by_id(ticket_id)
        
        if not ticket:
            return None
        
        if title is not None:
            ticket.title = title
        
        if status is not None:
            ticket.status = status
            
            # Si se cierra, marcar fecha
            if status == TicketStatus.CLOSED and not ticket.closed_at:
                ticket.closed_at = datetime.utcnow()
            
            # Si se escala, marcar fecha
            if status == TicketStatus.ESCALATED and not ticket.escalated_at:
                ticket.escalated_at = datetime.utcnow()
        
        if priority is not None:
            ticket.priority = priority
        
        if category is not None:
            ticket.category = category
        
        try:
            self.db.commit()
            self.db.refresh(ticket)
            return ticket
        except Exception:
            self.db.rollback()
            return None
    
    def escalate(self, ticket_id: UUID) -> Optional[Ticket]:
        """
        Escala un ticket a humano.
        
        Returns:
            Ticket escalado o None si no existe.
        """
        return self.update(ticket_id, status=TicketStatus.ESCALATED)
    
    def close(self, ticket_id: UUID) -> Optional[Ticket]:
        """
        Cierra un ticket.
        
        Returns:
            Ticket cerrado o None si no existe.
        """
        return self.update(ticket_id, status=TicketStatus.CLOSED)
    
    def list_by_user(
        self,
        user_id: UUID,
        status: Optional[TicketStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Ticket]:
        """
        Lista tickets de un usuario con filtros opcionales.
        
        Args:
            user_id: ID del usuario
            status: Filtrar por estado (opcional)
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
        """
        query = self.db.query(Ticket).filter(Ticket.user_id == user_id)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_by_user(self, user_id: UUID, status: Optional[TicketStatus] = None) -> int:
        """Cuenta tickets de un usuario con filtro opcional de estado."""
        query = self.db.query(Ticket).filter(Ticket.user_id == user_id)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        return query.count()
    
    def list_all(
        self,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Ticket]:
        """
        Lista todos los tickets con filtros opcionales (para admins).
        """
        query = self.db.query(Ticket)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        if priority:
            query = query.filter(Ticket.priority == priority)
        
        return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_all(
        self,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None
    ) -> int:
        """Cuenta todos los tickets con filtros opcionales."""
        query = self.db.query(Ticket)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        if priority:
            query = query.filter(Ticket.priority == priority)
        
        return query.count()