"""
Endpoints para gestión de tickets.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from db import get_db
from db.repository import TicketRepository, UserRepository
from db.models import TicketStatus, TicketPriority
from schemas import TicketCreate, TicketUpdate, TicketResponse, TicketListResponse
from core.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo ticket para el usuario autenticado.
    
    - **title**: Título del ticket (mínimo 3 caracteres)
    - **category**: Categoría del ticket (opcional)
    """
    repo = TicketRepository(db)
    
    ticket = repo.create(
        user_id=UUID(user_id),
        title=ticket_data.title,
        category=ticket_data.category
    )
    
    # Añadir conteo de mensajes
    response = TicketResponse.model_validate(ticket)
    response.message_count = ticket.message_count
    
    return response


@router.get("/", response_model=TicketListResponse)
async def list_my_tickets(
    status_filter: TicketStatus = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista los tickets del usuario autenticado.
    
    - **status_filter**: Filtrar por estado (opcional)
    - **page**: Número de página (default: 1)
    - **page_size**: Registros por página (default: 20, max: 100)
    """
    repo = TicketRepository(db)
    
    skip = (page - 1) * page_size
    
    tickets = repo.list_by_user(
        user_id=UUID(user_id),
        status=status_filter,
        skip=skip,
        limit=page_size
    )
    
    total = repo.count_by_user(UUID(user_id), status=status_filter)
    
    # Añadir conteo de mensajes a cada ticket
    tickets_response = []
    for ticket in tickets:
        ticket_data = TicketResponse.model_validate(ticket)
        ticket_data.message_count = ticket.message_count
        tickets_response.append(ticket_data)
    
    return TicketListResponse(
        tickets=tickets_response,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene un ticket específico.
    
    Solo el propietario del ticket puede verlo.
    """
    repo = TicketRepository(db)
    
    ticket = repo.get_by_id(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Verificar que el usuario sea el propietario
    if str(ticket.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este ticket"
        )
    
    response = TicketResponse.model_validate(ticket)
    response.message_count = ticket.message_count
    
    return response


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: UUID,
    ticket_update: TicketUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Actualiza un ticket.
    
    Solo el propietario puede actualizar el ticket.
    Campos opcionales: title, status, priority, category
    """
    ticket_repo = TicketRepository(db)
    
    # Verificar que el ticket existe y pertenece al usuario
    ticket = ticket_repo.get_by_id(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    if str(ticket.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este ticket"
        )
    
    # Actualizar ticket
    updated_ticket = ticket_repo.update(
        ticket_id=ticket_id,
        title=ticket_update.title,
        status=ticket_update.status,
        priority=ticket_update.priority,
        category=ticket_update.category
    )
    
    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el ticket"
        )
    
    response = TicketResponse.model_validate(updated_ticket)
    response.message_count = updated_ticket.message_count
    
    return response


@router.post("/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cierra un ticket.
    
    Marca el ticket como cerrado y registra la fecha de cierre.
    """
    ticket_repo = TicketRepository(db)
    
    # Verificar que el ticket existe y pertenece al usuario
    ticket = ticket_repo.get_by_id(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    if str(ticket.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para cerrar este ticket"
        )
    
    # Cerrar ticket
    closed_ticket = ticket_repo.close(ticket_id)
    
    if not closed_ticket:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar el ticket"
        )
    
    response = TicketResponse.model_validate(closed_ticket)
    response.message_count = closed_ticket.message_count
    
    return response