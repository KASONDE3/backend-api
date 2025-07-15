from pydantic import BaseModel, ConfigDict

class TechnicianOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    
    model_config = ConfigDict(from_attributes=True)