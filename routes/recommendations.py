from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
    new_recommendation = Recommendation(**recommendation.dict())
    db.add(new_recommendation)
    await db.commit()
    await db.refresh(new_recommendation)
    return new_recommendation

@router.get("/", response_model=List[RecommendationOut])
async def get_all_recommendations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recommendation))
    return result.scalars().all()

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