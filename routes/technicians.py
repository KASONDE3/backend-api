# routers/users.py or routers/technicians.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.ticketModels import User, Ticket, Status 
from db import get_db  
from models.technicians import TechnicianOut  
from sqlalchemy import func, case

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




@router.get("/technicians/with-ticket-stats")
async def get_technicians_with_ticket_stats(db: AsyncSession = Depends(get_db)):
    # Count tickets by status for each technician
    open_count = func.sum(case((Status.name == "open", 1), else_=0)).label("open_tickets")
    in_progress_count = func.sum(case((Status.name == "in-progress", 1), else_=0)).label("in_progress_tickets")
    completed_count = func.sum(case((Status.name == "completed", 1), else_=0)).label("completed_tickets")

    query = (
        select(
            User.user_id,
            User.first_name,
            User.last_name,
            User.email,
            open_count,
            in_progress_count,
            completed_count,
        )
        .select_from(User)
        .join(Ticket, Ticket.assigned_to == User.user_id, isouter=True)
        .join(Status, Status.status_id == Ticket.status_id, isouter=True)
        .where(User.role == "technician")
        .group_by(User.user_id, User.first_name, User.last_name, User.email)
        .order_by(User.first_name.asc(), User.last_name.asc())
    )

    result = await db.execute(query)
    rows = result.all()

    technicians = []
    for row in rows:
        technicians.append({
            "user_id": row.user_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "open_tickets": int(row.open_tickets or 0),
            "in_progress_tickets": int(row.in_progress_tickets or 0),
            "completed_tickets": int(row.completed_tickets or 0),
        })

    return technicians

