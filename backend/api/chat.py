"""
Endpoints para chat (mensajes dentro de tickets).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from db import get_db
from db.repository import TicketRepository, MessageRepository
from db.models import MessageRole
from schemas import MessageCreate, MessageResponse, ChatHistoryResponse
from core.security import get_current_user_id

router = APIRouter()


@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    ticket_id: UUID,
    message_data: MessageCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Envía un mensaje del usuario en un ticket.
    
    - **ticket_id**: ID del ticket
    - **content**: Contenido del mensaje
    
    Por ahora solo crea el mensaje del usuario.
    En el futuro, aquí se invocará al agente para generar la respuesta.
    """
    ticket_repo = TicketRepository(db)
    message_repo = MessageRepository(db)
    
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
            detail="No tienes permiso para escribir en este ticket"
        )
    
    # Verificar que el ticket no esté cerrado
    if not ticket.is_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes enviar mensajes en un ticket cerrado"
        )
    
    # Crear mensaje del usuario
    message = message_repo.create_user_message(
        ticket_id=ticket_id,
        content=message_data.content
    )
    
    # TODO: Aquí se invocará al agente para generar la respuesta automática
    # Por ahora, solo devolvemos el mensaje del usuario
    
    return message


@router.get("/{ticket_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial completo de mensajes de un ticket.
    
    - **ticket_id**: ID del ticket
    
    Retorna todos los mensajes ordenados cronológicamente.
    """
    ticket_repo = TicketRepository(db)
    message_repo = MessageRepository(db)
    
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
            detail="No tienes permiso para ver este chat"
        )
    
    # Obtener mensajes
    messages = message_repo.list_by_ticket(ticket_id)
    total = message_repo.count_by_ticket(ticket_id)
    
    return ChatHistoryResponse(
        ticket_id=ticket_id,
        messages=messages,
        total_messages=total
    )


@router.get("/{ticket_id}/conversation", response_model=dict)
async def get_conversation_for_agent(
    ticket_id: UUID,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de conversación en formato para el agente.
    
    - **ticket_id**: ID del ticket
    - **limit**: Limitar a los últimos N mensajes (default: 20)
    
    Retorna mensajes en formato: [{"role": "user|assistant", "content": "..."}]
    Útil para enviar al agente LLM.
    """
    ticket_repo = TicketRepository(db)
    message_repo = MessageRepository(db)
    
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
            detail="No tienes permiso para ver esta conversación"
        )
    
    # Obtener conversación en formato para el agente
    conversation = message_repo.get_conversation_history(ticket_id, limit=limit)
    
    return {
        "ticket_id": str(ticket_id),
        "messages": conversation,
        "count": len(conversation)
    }