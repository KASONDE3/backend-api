import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from db import Base
from sqlalchemy.orm import relationship

# --- SQLAlchemy Models ---

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    other_name = Column(String(255), nullable=True)
    last_name = Column(String(255))
    nrc = Column(String(255))
    role = Column(String(20), nullable=False)
    department = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    assigned_tickets = relationship(
        "Ticket",
        back_populates="technician",
        foreign_keys="Ticket.assigned_to"
    )
    created_tickets = relationship(
        "Ticket",
        back_populates="user",
        foreign_keys="Ticket.user_id"
    )


class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    status_id = Column(Integer, ForeignKey("statuses.status_id"))
    category_id = Column(Integer, ForeignKey("ticket_categories.category_id"))
    priority_id = Column(Integer, ForeignKey("ticket_priorities.priority_id"))
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    # Relationships
    technician = relationship(
        "User",
        back_populates="assigned_tickets",
        foreign_keys=[assigned_to]
    )
    user = relationship(
        "User",
        back_populates="created_tickets",
        foreign_keys=[user_id]
    )
    status = relationship(
        "Status",
        back_populates="tickets",
        foreign_keys=[status_id]
    )


class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)


class TicketPriority(Base):
    __tablename__ = "ticket_priorities"
    priority_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    response_time = Column(Integer, nullable=False)


class Status(Base):
    __tablename__ = "statuses"
    status_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    # Optional reverse relationship to tickets
    tickets = relationship("Ticket", back_populates="status")  # ✅ This is valid

    

# --- Pydantic Schemas ---

class TicketOut(BaseModel):
    ticket_id: int
    user_id: int
    category_id: int
    assigned_to: Optional[int]
    status_id: int
    priority_id: int
    title: str
    description: Optional[str]
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]  

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class TicketCreate(BaseModel):
    email: str
    title: str
    description: str
    priority_id: int
    category_id: int
    status_id: int
    assigned_to: Optional[int] = None


class TicketStatusUpdate(BaseModel):
    status_id: int


class TicketUpdate(BaseModel):
    ticket_id: int
    assigned_to: int
    new_status_id: int


class TicketResponse(BaseModel):
    ticket_id: int
    title: str
    description: Optional[str]
    status_id: int
    assigned_to: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class PriorityOut(BaseModel):
    priority_id: int
    name: str


class CategoryOut(BaseModel):
    category_id: int
    name: str


class StatusOut(BaseModel):
    status_id: int
    name: str
