# schemas/technician_schemas.py

from pydantic import BaseModel

class TechnicianOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
