from pydantic import BaseModel

class PriorityOut(BaseModel):
    priority_id: int
    name: str

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    category_id: int
    name: str

    class Config:
        orm_mode = True


class StatusOut(BaseModel):
    status_id: int
    name: str

    class Config:
        orm_mode = True
