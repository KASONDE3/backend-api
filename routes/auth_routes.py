from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext

from db import get_db
from models.auth_model import Auth
from models.ticketModels import User
from schemas.auth_schemas import AuthCreate, AuthLogin, AuthOut

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# List all registered users
@router.get("/all", response_model=list[AuthOut])
async def list_registered_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth))
    users = result.scalars().all()
    return users

# Update password
@router.put("/update-password")
async def update_password(auth_data: AuthCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth).where(Auth.email == auth_data.email))
    auth_entry = result.scalars().first()

    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    auth_entry.password_hash = hash_password(auth_data.password)
    await db.commit()
    return {"message": "Password updated successfully"}

# Delete account
@router.delete("/delete/{email}")
async def delete_user(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth).where(Auth.email == email))
    auth_entry = result.scalars().first()

    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(auth_entry)
    await db.commit()
    return {"message": f"User {email} deleted"}
