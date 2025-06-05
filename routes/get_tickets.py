from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from db import get_db
from models.getTickets import Ticket, User, Category, Priority, Status

router = APIRouter(prefix="/tickets", tags=["Get All Tickets"])
router = APIRouter()

@router.get("/")
async def list_tickets(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    category: int = None,
    priority: int = None,
    status: int = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Ticket).options(
        joinedload(Ticket.category),
        joinedload(Ticket.priority),
        joinedload(Ticket.status),
        joinedload(Ticket.user)
    )
    if category:
        query = query.where(Ticket.category_id == category)
    if priority:
        query = query.where(Ticket.priority_id == priority)
    if status:
        query = query.where(Ticket.status_id == status)

    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    paginated_query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(paginated_query)
    tickets = result.scalars().unique().all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "tickets": [
            {
                "id": t.ticket_id,
                "title": t.title,
                "description": t.description,
                "category": t.category.name if t.category else None,
                "priority": t.priority.level if t.priority else None,
                "status": t.status.state if t.status else None,
                "user": t.user.name if t.user else None,
                "email": t.user.email if t.user else None
            } for t in tickets
        ]
    }

@router.post("/create")
async def create_ticket(ticket: dict, db: AsyncSession = Depends(get_db)):
    email = ticket.get("email")
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="User with email not found")

    new_ticket = Ticket(
        title=ticket["title"],
        description=ticket["description"],
        status_id=ticket["status_id"],
        category_id=ticket["category_id"],
        priority_id=ticket["priority_id"],
        assigned_to=ticket["assigned_to"],
        user_id=user.user_id,
    )
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return {"message": "Ticket created", "ticket_id": new_ticket.ticket_id}
