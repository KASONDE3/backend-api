from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.ticketModels import Ticket
from models.ticketModels import User 
from db import get_db
from models.ticket_status_models import TicketStatusDetailResponse

router = APIRouter()

@router.get("/status/{ticket_id}", response_model=TicketStatusDetailResponse)
async def get_ticket_status(ticket_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.status),
            selectinload(Ticket.technician),
            selectinload(Ticket.user)  # 👈 now works properly
        )
        .where(Ticket.ticket_id == ticket_id)
    )
    ticket = result.scalars().first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    technician_name = None
    if ticket.technician:
        technician_name = f"{ticket.technician.first_name} {ticket.technician.last_name}"

    created_by_email = ticket.user.email if ticket.user else None
    created_by_full_name = f"{ticket.user.first_name} {ticket.user.last_name}" if ticket.user else None
    department = ticket.user.department if ticket.user else None

    return {
        "ticket_id": ticket.ticket_id,
        "status": ticket.status.name,
        "created_at": ticket.created_at,
        "technician": technician_name,
        "created_by_email": created_by_email,
        "created_by_name": created_by_full_name,
        "department": department
    }
