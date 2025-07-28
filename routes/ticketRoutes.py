from email.message import EmailMessage
import os
from typing import List, Optional
import aiosmtplib
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from db import get_async_session
from db import get_db
from schemas.ticketSchemas import TicketCreate, FullTicketResponse
from models.ticketModels import TicketOut, TicketResponse, TicketUpdate, User, Ticket, TicketCategory, TicketPriority, Status
from db import get_async_session
from sqlalchemy.orm import selectinload

router = APIRouter()

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
@router.get("/all", response_model=List[TicketOut])
async def get_all_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket))
    tickets = result.scalars().all()
    return tickets

@router.get("/{ticket_id}", response_model=FullTicketResponse)
async def get_ticket_by_id(
    ticket_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.user),
            selectinload(Ticket.technician)
        )
        .where(Ticket.ticket_id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "ticket_id": ticket.ticket_id,
        "user_id": ticket.user_id,
        "category_id": ticket.category_id,
        "assigned_to": ticket.assigned_to,
        "status_id": ticket.status_id,
        "priority_id": ticket.priority_id,
        "title": ticket.title,
        "description": ticket.description,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "user_email": ticket.user.email if ticket.user else None,
        "created_by_name": f"{ticket.user.first_name} {ticket.user.last_name}" if ticket.user else None,
        "department": ticket.user.department if ticket.user else None,
        "technician_name": f"{ticket.technician.first_name} {ticket.technician.last_name}" if ticket.technician else None
    }


## Ticket with Email Sending 
@router.post("/create")
async def create_ticket(ticket_data: TicketCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if user exists
    result = await db.execute(select(User).where(User.email == ticket_data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Check if technician exists
    technician = None
    if ticket_data.assigned_to:
        result = await db.execute(select(User).where(User.user_id == ticket_data.assigned_to))
        technician = result.scalars().first()

    # 3. Create the ticket
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

    # 4. Send email to technician (if assigned)
    if technician:
        await send_email_to_technician(
            technician_email=technician.email,
            technician_name=technician.first_name,
            ticket_title=new_ticket.title,
            ticket_description=new_ticket.description
        )

    return {
        "message": "Ticket created successfully",
        "ticket_id": new_ticket.ticket_id
    }

# Email sending function
async def send_email_to_technician(technician_email, technician_name, ticket_title, ticket_description):
    system_email = os.getenv("SYSTEM_EMAIL_ADDRESS")
    system_password = os.getenv("SYSTEM_EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    message = EmailMessage()
    message["From"] = system_email
    message["To"] = technician_email
    message["Subject"] = f"New Ticket Assigned: {ticket_title}"

    message.set_content(f"""
Hi {technician_name},

A new ticket has been assigned to you.

Title: {ticket_title}
Description: {ticket_description}

Please log in to the support system to view more details.

Best regards,
IT Support System
""")

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=system_email,
            password=system_password
        )
    except Exception as e:
        print(f"Failed to send email to technician: {e}")

# Email sending function for notifying the ticket creator
async def send_email_to_user(user_email, user_name, ticket_title, new_status):
    system_email = os.getenv("SYSTEM_EMAIL_ADDRESS")
    system_password = os.getenv("SYSTEM_EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    message = EmailMessage()
    message["From"] = system_email
    message["To"] = user_email
    message["Subject"] = f"Your Ticket Status Updated: {ticket_title}"

    message.set_content(f"""
Hi {user_name},

The status of your ticket '{ticket_title}' has been updated to: {new_status}

Please log in to the support system to view more details.

Best regards,
IT Support System
""")

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=system_email,
            password=system_password
        )
    except Exception as e:
        print(f"Failed to send email to user: {e}")

@router.put("/update-status", response_model=TicketResponse)
async def update_ticket_status(payload: TicketUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Ticket)
        .options(selectinload(Ticket.user))
        .where(Ticket.ticket_id == payload.ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.assigned_to != payload.assigned_to:
        raise HTTPException(status_code=403, detail="You are not authorized to update this ticket")

    ticket.status_id = payload.new_status_id
    await db.commit()
    await db.refresh(ticket)

    # Send email to the user who created the ticket
    if ticket.user:
        user_email = ticket.user.email
        user_name = f"{ticket.user.first_name} {ticket.user.last_name}"
        ticket_title = ticket.title
        # Get new status name
        status_result = await db.execute(select(Status).where(Status.status_id == ticket.status_id))
        status_obj = status_result.scalar_one_or_none()
        new_status_name = status_obj.name if status_obj else str(ticket.status_id)
        await send_email_to_user(user_email, user_name, ticket_title, new_status_name)

    return ticket