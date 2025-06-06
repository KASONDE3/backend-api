from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from db import get_async_session
from db import get_db
from schemas.ticketSchemas import TicketCreate
from models.ticketModels import TicketOut, User, Ticket, TicketCategory, TicketPriority, Status
from db import get_async_session

router = APIRouter()


@router.get("/all", response_model=List[TicketOut])
async def get_all_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket))
    tickets = result.scalars().all()
    return tickets

@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket_by_id(
    ticket_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/create")
async def create_ticket(ticket_data: TicketCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == ticket_data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create ticket
    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        user_id=user.user_id,
        status_id=ticket_data.status_id,
        category_id=ticket_data.category_id,
        priority_id=ticket_data.priority_id,
        assigned_to=ticket_data.assigned_to
    )
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)

    return {
        "message": "Ticket created successfully",
        "ticket_id": new_ticket.ticket_id
    }


@router.get("/verify-email")
async def verify_email(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }


@router.get("/priorities")
async def get_priorities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketPriority))
    return result.scalars().all()


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketCategory))
    return result.scalars().all()


@router.get("/statuses")
async def get_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Status))
    return result.scalars().all()