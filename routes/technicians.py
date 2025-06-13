# routers/users.py or routers/technicians.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.ticketModels import User 
from db import get_db  
from models.technicians import TechnicianOut  

router = APIRouter()

@router.get("/technicians", response_model=list[TechnicianOut])
async def get_technicians(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.role == "technician")
    )
    technicians = result.scalars().all()
    return technicians
