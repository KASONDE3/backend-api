# models/ticket_response_models.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketStatusDetailResponse(BaseModel):
    ticket_id: int
    status: str
    created_at: datetime
    technician: Optional[str] = None  # technician may be unassigned

    class Config:
        from_attributes = True
