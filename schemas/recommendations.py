from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class RecommendationCreate(BaseModel):
    ticket_id: int
    recommendation: str
    created_by: int

class RecommendationUpdate(BaseModel):
    recommendation: str

class RecommendationOut(BaseModel):
    recomm_id: int
    ticket_id: int
    recommendation: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 