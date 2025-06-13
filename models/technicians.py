from pydantic import BaseModel

class TechnicianOut(BaseModel):
    user_id: int
    first_name: str
    last_name:str
    
    class config: orm_model = True