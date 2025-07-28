# routers/technician_routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import exists
from sqlalchemy.orm import aliased
from db import get_db
from models.ticketModels import User, Ticket
from schemas.dynamic_technician import TechnicianOut

router = APIRouter()

@router.get("/unassigned-technicians", response_model=list[TechnicianOut])
async def get_unassigned_technicians(db: AsyncSession = Depends(get_db)):
    # Subquery: All technician user_ids with tickets assigned
    subq = select(Ticket.assigned_to).where(Ticket.assigned_to != None).distinct()

    # Main query: All users who are technicians and not in the above subquery
    result = await db.execute(
        select(User)
        .where(User.role == "technician")
        .where(User.user_id.not_in(subq))
    )
    technicians = result.scalars().all()
    return technicians
