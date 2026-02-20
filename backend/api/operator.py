"""
Endpoints para operadores/administradores del helpdesk.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from db import get_db
from db.repository import TicketRepository, MessageRepository
from db.models import TicketStatus
from schemas.ticket import TicketResponse, TicketListResponse
from schemas.message import MessageCreate, MessageResponse
from core.security import get_current_user_id

router = APIRouter(prefix="/api/operator", tags=["operator"])


def get_current_admin_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Dependency para verificar que el usuario es admin."""
    from db.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de operador"
        )
    
    return user_id


@router.get("/tickets", response_model=TicketListResponse)
async def list_operator_tickets(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los tickets para operadores.
    
    Por defecto muestra tickets escalados y en progreso.
    Los operadores pueden ver tickets de todos los usuarios.
    """
    from db.models import Ticket
    
    # Si no se especifica filtro, mostrar escalados y en progreso
    if not status_filter:
        query = db.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.ESCALATED, TicketStatus.IN_PROGRESS])
        )
    else:
        # Parsear filtro de status (puede ser múltiple separado por comas)
        statuses = [s.strip().upper() for s in status_filter.split(',')]
        query = db.query(Ticket).filter(Ticket.status.in_(statuses))
    
    # Ordenar por más reciente primero
    query = query.order_by(Ticket.created_at.desc())
    
    # Contar total
    total = query.count()
    
    # Paginación
    offset = (page - 1) * page_size
    tickets = query.offset(offset).limit(page_size).all()
    
    # El message_count ya es una property del modelo Ticket
    # No necesitamos calcularlo manualmente
    
    return TicketListResponse(
        tickets=tickets,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_operator_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un ticket específico (cualquier usuario).
    Solo para operadores.
    """
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get_by_id(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    return ticket


@router.post("/tickets/{ticket_id}/take", response_model=TicketResponse)
async def take_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    El operador toma un ticket escalado y lo marca como "en progreso".
    """
    ticket_repo = TicketRepository(db)
    message_repo = MessageRepository(db)
    
    ticket = ticket_repo.get_by_id(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Cambiar status a IN_PROGRESS
    updated_ticket = ticket_repo.update(
        ticket_id=ticket_id,
        status=TicketStatus.IN_PROGRESS
    )
    
    # Crear mensaje del sistema indicando que un operador lo tomó
    message_repo.create_system_message(
        ticket_id=ticket_id,
        content="👤 Un operador humano ha tomado esta consulta y te responderá pronto."
    )
    
    return updated_ticket


@router.post("/tickets/{ticket_id}/respond", response_model=MessageResponse)
async def operator_respond(
    ticket_id: UUID,
    message_data: MessageCreate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    El operador envía una respuesta al usuario.
    Se guarda como mensaje del asistente pero con metadata indicando que es humano.
    """
    ticket_repo = TicketRepository(db)
    message_repo = MessageRepository(db)
    
    ticket = ticket_repo.get_by_id(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Crear mensaje del asistente pero indicando que es respuesta humana
    message = message_repo.create_assistant_message(
        ticket_id=ticket_id,
        content=message_data.content,
        metadata={
            "human_response": True,
            "operator_id": user_id
        }
    )
    
    return message


@router.get("/stats")
async def get_operator_stats(
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Estadísticas para el dashboard del operador.
    """
    from db.models import Ticket
    
    escalated_count = db.query(Ticket).filter(
        Ticket.status == TicketStatus.ESCALATED
    ).count()
    
    in_progress_count = db.query(Ticket).filter(
        Ticket.status == TicketStatus.IN_PROGRESS
    ).count()
    
    open_count = db.query(Ticket).filter(
        Ticket.status == TicketStatus.OPEN
    ).count()
    
    total_count = db.query(Ticket).count()
    
    return {
        "escalated": escalated_count,
        "in_progress": in_progress_count,
        "open": open_count,
        "total": total_count
    }