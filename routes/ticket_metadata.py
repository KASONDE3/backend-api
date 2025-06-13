from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from models.ticketModels import TicketPriority, TicketCategory, Status 
from models.ticket_metadata import PriorityOut, CategoryOut, StatusOut
from db import get_db  

router = APIRouter()

@router.get("/ticket-priorities", response_model=List[PriorityOut])
async def get_ticket_priorities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketPriority))
    return result.scalars().all()

@router.get("/ticket-categories", response_model=List[CategoryOut])
async def get_ticket_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketCategory))
    return result.scalars().all()

@router.get("/ticket-statuses", response_model=List[StatusOut])
async def get_ticket_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Status))
    return result.scalars().all()
