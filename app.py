from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from db import engine, Base, get_db
from routes import ticket_metadata
from routes.ticketRoutes import router as ticket_router
from routes.MetaRoutes import router as meta_router
from routes.technicians import router as techician_router
from routes.ticket_status import router as ticket_status
from routes.dynamic_technician import router as dynamic_technician
from routes.auth_routes import router as auth_router
from routes.recommendations import router as recommendations_router

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
app.include_router(ticket_metadata.router)
app.include_router(techician_router, prefix="/users", tags=["Technicians"])
app.include_router(ticket_status, prefix="/status", tags=["TicketStatus"])
app.include_router(dynamic_technician, prefix="/dynamic_technician", tags=["dynamic_technician"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(recommendations_router, prefix="/Recommendations", tags=["Recommendations"])