from pydantic import BaseModel, ConfigDict

class PriorityOut(BaseModel):
    priority_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryOut(BaseModel):
    category_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StatusOut(BaseModel):
    status_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
