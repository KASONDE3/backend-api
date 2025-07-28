# routers/users.py or routers/technicians.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.ticketModels import User 
from db import get_db  
from models.technicians import TechnicianOut  
from sqlalchemy import func

router = APIRouter()

#@router.get("/technicians", response_model=list[TechnicianOut])
#async def get_technicians(db: AsyncSession = Depends(get_db)):
 #   result = await db.execute(
  #      select(User).where(User.role == "technician")
   ##technicians = result.scalars().all()
    #return technicians

@router.get("/technicians", response_model=TechnicianOut)
async def get_technician_with_lowest_load(db: AsyncSession = Depends(get_db)):
    # Subquery: count assigned tickets for each technician
    subq = (
        select(
            User.user_id,
            func.count().label("ticket_count")
        )
        .select_from(User)
        .join(User.assigned_tickets, isouter=True)
        .where(User.role == "technician")
        .group_by(User.user_id)
        .subquery()
    )

    # Select the technician with the lowest ticket_count
    result = await db.execute(
        select(User)
        .join(subq, User.user_id == subq.c.user_id)
        .order_by(subq.c.ticket_count.asc())
        .limit(1)
    )
    technician = result.scalars().first()
    if not technician:
        return None
    return technician
