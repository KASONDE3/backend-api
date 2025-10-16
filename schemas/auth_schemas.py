from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class Token(BaseModel):
    access_token: str
    refresh_token: str
    email: str

class AuthCreate(BaseModel):
    email: str
    password: str
    is_approved: Optional[bool] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthOut(BaseModel):
    auth_id: int
    email: str
    is_approved: Optional[bool] = None


    model_config = ConfigDict(from_attributes=True)

class TokenPayload(BaseModel):
    refresh_token: str

class LoginInput(BaseModel):
    email: str
    password: str


class AuthUpdate(BaseModel):
    # Identify the record by current email
    current_email: str
    # Optional fields to update
    new_email: Optional[str] = None
    is_approved: Optional[bool] = None
