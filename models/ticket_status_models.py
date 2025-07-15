# models/ticket_status_models.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import datetime

class TicketStatusDetailResponse(BaseModel):
    ticket_id: int
    status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    technician: Optional[str]
    created_by_email: Optional[str]
    created_by_name: Optional[str]
    department: Optional[str]

    model_config = ConfigDict(from_attributes=True)
