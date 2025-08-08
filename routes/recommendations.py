from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from db import get_db
from models.recommendations_models import Recommendation
from schemas.recommendations import RecommendationCreate, RecommendationUpdate, RecommendationOut
from typing import List

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/", response_model=RecommendationOut)
async def create_recommendation(
    recommendation: RecommendationCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate that the user exists
        from models.auth_model import Auth
        user_result = await db.execute(select(Auth).where(Auth.auth_id == recommendation.created_by))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=400, 
                detail=f"User with ID {recommendation.created_by} does not exist"
            )
        
        # Validate that the ticket exists
        from models.ticketModels import Ticket
        ticket_result = await db.execute(select(Ticket).where(Ticket.ticket_id == recommendation.ticket_id))
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            raise HTTPException(
                status_code=400, 
                detail=f"Ticket with ID {recommendation.ticket_id} does not exist"
            )
        
        new_recommendation = Recommendation(**recommendation.dict())
        db.add(new_recommendation)
        await db.commit()
        await db.refresh(new_recommendation)
        return new_recommendation
    
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[RecommendationOut])
async def get_all_recommendations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recommendation))
    return result.scalars().all()

# route for get recommendation by ticket_id
@router.get("/ticket/{ticket_id}", response_model=List[RecommendationOut])
async def get_recommendations_by_ticket(
    ticket_id: int, db: AsyncSession = Depends(get_db)
    ):
    result = await db.execute(select(Recommendation).where(Recommendation.ticket_id == ticket_id
    ))
    recommendations = result.scalars().all()
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found for this ticket")
    return recommendations

@router.get("/{recomm_id}", response_model=RecommendationOut)
async def get_recommendation_by_id(
    recomm_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Recommendation).where(Recommendation.recomm_id == recomm_id))
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation

@router.put("/{recomm_id}", response_model=RecommendationOut)
async def update_recommendation(
    recomm_id: int,
    recommendation_update: RecommendationUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Recommendation).where(Recommendation.recomm_id == recomm_id))
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    recommendation.recommendation = recommendation_update.recommendation
    await db.commit()
    await db.refresh(recommendation)
    return recommendation

@router.delete("/{recomm_id}")
async def delete_recommendation(
    recomm_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Recommendation).where(Recommendation.recomm_id == recomm_id))
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    await db.delete(recommendation)
    await db.commit()
    return {"message": "Recommendation deleted"}
