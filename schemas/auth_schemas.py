from pydantic import BaseModel, EmailStr

class AuthCreate(BaseModel):
    email: EmailStr
    password: str

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

class AuthOut(BaseModel):
    auth_id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    user_id: int
    email: str
    role: str
    first_name: str