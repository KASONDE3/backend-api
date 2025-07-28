from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# Import all models here to register them with the Base
from models.auth_model import Auth
from models.ticketModels import User, Ticket
from models.recommendations_models import Recommendation


# Dependency
async def get_db() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session
        
async def get_async_session() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session
