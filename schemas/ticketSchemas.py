from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class TicketCreate(BaseModel):
    email: EmailStr
    title: str
    description: str
    status_id: int
    category_id: int
    priority_id: int
    assigned_to: Optional[int] = None
    
class FullTicketResponse(BaseModel):
    ticket_id: int
    user_id: int
    category_id: int
    assigned_to: Optional[int]
    status_id: int
    priority_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    user_email: str
    created_by_name: str
    department: str
    technician_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)

