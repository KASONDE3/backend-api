from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from schemas.auth_schemas import LoginInput, AuthOut, Token, LoginRequest
from db import get_db
from models.auth_model import Auth
from models.ticketModels import User
from schemas.auth_schemas import AuthCreate, AuthOut, Token, TokenPayload
from utils.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_user_role,
    require_role,
)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 🔐 Register
@router.post("/register", response_model=AuthOut)  # AuthOut should at least include email
async def register(auth_data: AuthCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Auth).where(Auth.email == auth_data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(auth_data.password)
    new_user = Auth(email=auth_data.email, password_hash=hashed)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# 🔐 Login
@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Auth).where(Auth.email == login_data.email))
    user = result.scalars().first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Get user profile information from users table
    user_profile = await db.execute(select(User).where(User.email == user.email))
    profile = user_profile.scalars().first()

    # Prepare token data with all required fields
    token_data = {
        "sub": user.email,
        "email": user.email,
        "role": profile.role if profile else None,
        "department": profile.department if profile else None,
        "first_name": profile.first_name if profile else None,
        "last_name": profile.last_name if profile else None
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        email=user.email
    )


# 🔁 Refresh Token
@router.post("/refresh", response_model=Token)
async def refresh_token(payload: TokenPayload, db: AsyncSession = Depends(get_db)):
    try:
        token_data = verify_token(payload.refresh_token)
        email = token_data.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        result = await db.execute(select(Auth).where(Auth.email == email))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Get user profile information from users table
        user_profile = await db.execute(select(User).where(User.email == user.email))
        profile = user_profile.scalars().first()

        # Prepare token data with all required fields
        new_token_data = {
            "sub": user.email,
            "email": user.email,
            "role": profile.role if profile else None,
            "department": profile.department if profile else None,
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None
        }

        new_access_token = create_access_token(new_token_data)
        new_refresh_token = create_refresh_token(new_token_data)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            email=user.email
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# 👤 Get current user
@router.get("/me", response_model=AuthOut)
async def get_me(current_user: Auth = Depends(get_current_user)):
    return current_user


# 🔒 List all users
@router.get("/all", response_model=list[AuthOut])
async def list_registered_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth))
    users = result.scalars().all()
    return users


# 🔄 Update password
@router.put("/update-password")
async def update_password(auth_data: AuthCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth).where(Auth.email == auth_data.email))
    auth_entry = result.scalars().first()

    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    auth_entry.password_hash = hash_password(auth_data.password)
    await db.commit()
    return {"message": "Password updated successfully"}


# ❌ Delete user
@router.delete("/delete/{email}")
async def delete_user(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth).where(Auth.email == email))
    auth_entry = result.scalars().first()

    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(auth_entry)
    await db.commit()
    return {"message": f"User {email} deleted"}


# 🔐 Role-based authorization examples
@router.get("/my-role")
async def get_my_role(current_role: str = Depends(get_current_user_role)):
    """Get the current user's role from their token"""
    return {"role": current_role}


@router.get("/admin-only")
async def admin_only_endpoint(current_role: str = Depends(require_role("admin"))):
    """Example endpoint that only admins can access"""
    return {"message": "Welcome admin!", "role": current_role}


@router.get("/technician-only")
async def technician_only_endpoint(current_role: str = Depends(require_role("technician"))):
    """Example endpoint that only technicians can access"""
    return {"message": "Welcome technician!", "role": current_role}
