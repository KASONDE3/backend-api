from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from db import engine, Base, get_db
from routes.ticketRoutes import router as ticket_router
from routes.MetaRoutes import router as meta_router
from routes.get_tickets import router as getTickets

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Fully unrestricted
    allow_credentials=False,    # Required for wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {
            "message": "✅ IT Support Ticketing System API is running",
            "database": "Connected to async MySQL"
        }
    except SQLAlchemyError as e:
        return {
            "message": "⚠️ API is running, but DB connection failed",
            "database": f"Error: {str(e)}"
        }
## Rooutes 
app.include_router(ticket_router, prefix="/tickets", tags=["Tickets"])
app.include_router(meta_router, prefix="/api/meta", tags=["Meta"])
app.include_router(getTickets, prefix="/tickets", tags=["Get All Tickets"])