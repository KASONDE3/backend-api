from pydantic import BaseModel, EmailStr
from typing import Optional

class TicketCreate(BaseModel):
    email: EmailStr
    title: str
    description: str
    status_id: int
    category_id: int
    priority_id: int
    assigned_to: Optional[int] = None
