from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from models.dropdown_models import TicketCategory, TicketPriority, Status
from db import get_db  

router = APIRouter()

@router.get("/priorities", response_model=List[str])
async def get_priorities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketPriority.name))
    return [row[0] for row in result.all()]

@router.get("/categories", response_model=List[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketCategory.name))
    return [row[0] for row in result.all()]

@router.get("/statuses", response_model=List[str])
async def get_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Status.name))
    return [row[0] for row in result.all()]
