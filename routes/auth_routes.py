from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from schemas.auth_schemas import LoginInput, AuthOut, Token, LoginRequest
from db import get_db
from models.auth_model import Auth
from models.ticketModels import User
from models.access_logs import AccessLog
from schemas.auth_schemas import AuthCreate, AuthOut, Token, TokenPayload, AuthUpdate
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


async def log_access_event(
    db: AsyncSession,
    user_email: str,
    action: str,
    request: Request = None
):
    """Log access events (login/logout) to the access_logs table"""
    try:
        ip_address = None
        user_agent = None
        
        if request:
            # Get client IP address
            if request.client:
                ip_address = request.client.host
            # Get user agent
            user_agent = request.headers.get("user-agent")
        
        access_log = AccessLog(
            user_email=user_email,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(access_log)
        await db.commit()
    except Exception as e:
        # Log the error but don't fail the main operation
        print(f"Failed to log access event: {e}")
        await db.rollback()


# 🔐 Register
@router.post("/register", response_model=AuthOut)  # AuthOut should at least include email
async def register(auth_data: AuthCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Auth).where(Auth.email == auth_data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(auth_data.password)
    new_user = Auth(email=auth_data.email, password_hash=hashed, is_approved=False)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# Login
@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Auth).where(Auth.email == login_data.email))
    user = result.scalars().first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Get user profile information from users table
    user_profile = await db.execute(select(User).where(User.email == user.email))
    profile = user_profile.scalars().first()

    # Check approval status if available on profile or auth record
    is_approved = None
    if profile is not None and hasattr(profile, "is_approved"):
        try:
            is_approved = bool(getattr(profile, "is_approved"))
        except Exception:
            is_approved = None
    elif hasattr(user, "is_approved"):
        try:
            is_approved = bool(getattr(user, "is_approved"))
        except Exception:
            is_approved = None

    if is_approved is False:
        raise HTTPException(status_code=403, detail="Account not approved")

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

    # Log successful login
    await log_access_event(db, user.email, "login", request)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        email=user.email
    )


#  Refresh Token
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


# 🚪 Logout
@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Logout user and log the event"""
    # Try to get user from token, but don't fail if token is invalid
    user_email = None
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            token_data = verify_token(token)
            user_email = token_data.get("email") or token_data.get("sub")
    except Exception as e:
        # Token is invalid or missing, but we still want to log the logout attempt
        print(f"Logout: Could not extract user from token: {e}")
        pass
    
    # Log logout event (even if we couldn't get user email)
    if user_email:
        await log_access_event(db, user_email, "logout", request)
        print(f"Logged logout for user: {user_email}")
    else:
        # Log with a placeholder if we can't determine the user
        await log_access_event(db, "unknown_user", "logout", request)
        print("Logged logout for unknown user")
    
    return {"message": "Successfully logged out"}


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


# 🔄 Update registered auth (email/is_approved)
@router.put("/update-registered-user", response_model=AuthOut)
async def update_registered_user(update: AuthUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth).where(Auth.email == update.current_email))
    auth_entry = result.scalars().first()

    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    if update.new_email is not None:
        # Ensure new email not taken
        existing = await db.execute(select(Auth).where(Auth.email == update.new_email))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Email already in use")
        auth_entry.email = update.new_email

    if update.is_approved is not None:
        auth_entry.is_approved = update.is_approved

    await db.commit()
    await db.refresh(auth_entry)
    return auth_entry


# ❌ Delete registered auth by email
@router.delete("/registered/{email}")
async def delete_registered_user(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Auth).where(Auth.email == email))
    auth_entry = result.scalars().first()

    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(auth_entry)
    await db.commit()
    return {"message": f"Registered user {email} deleted"}

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


# 📊 Get total number of users
@router.get("/count")
async def get_user_count(db: AsyncSession = Depends(get_db)):
    """Get the total number of registered users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"total_users": len(users)}


# Get access logs (admin only)
@router.get("/access-logs")
async def get_access_logs(
    limit: int = 100,
    offset: int = 0,
    current_role: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Get access logs - admin only"""
    result = await db.execute(
        select(AccessLog)
        .order_by(AccessLog.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()
    
    return {
        "logs": [
            {
                "log_id": log.log_id,
                "user_email": log.user_email,
                "action": log.action,
                "timestamp": log.timestamp,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            }
            for log in logs
        ],
        "total_returned": len(logs)
    }