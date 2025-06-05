from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models.ticketModels import TicketCategory, TicketPriority, Status

router = APIRouter()

@router.get("/categories/")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketCategory))
    categories = result.scalars().all()
    return [{"id": c.id, "name": c.name} for c in categories]

@router.get("/priorities/")
async def get_priorities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketPriority))
    priorities = result.scalars().all()
    return [{"id": p.id, "level": p.level} for p in priorities]

@router.get("/statuses/")
async def get_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Status))
    statuses = result.scalars().all()
    return [{"id": s.id, "state": s.state} for s in statuses]
