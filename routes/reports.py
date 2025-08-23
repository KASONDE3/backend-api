from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
import os
import json
import httpx
from db import get_async_session
from models.ticketModels import Ticket
from models.ticketModels import TicketOut

router = APIRouter()

@router.get("/tickets/filter", response_model=List[TicketOut])
async def filter_tickets(
    category_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    query = select(Ticket)

    if category_id is not None:
        query = query.where(Ticket.category_id == category_id)
    if user_id is not None:
        query = query.where(Ticket.user_id == user_id)
    if title is not None:
        query = query.where(Ticket.title.ilike(f"%{title}%"))

    result = await db.execute(query)
    tickets = result.scalars().all()

    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found matching the criteria")

    return tickets

@router.get("/tickets/matching-criteria", response_model=List[TicketOut])
async def get_tickets_matching_criteria(
    db: AsyncSession = Depends(get_async_session)
):
    """
    Fetches all tickets and uses Gemini API to analyze and return tickets 
    with matching title, category_id, and user_id.
    """
    # Fetch all tickets from the database
    result = await db.execute(select(Ticket))
    all_tickets = result.scalars().all()
    
    if not all_tickets:
        raise HTTPException(status_code=404, detail="No tickets found in the system")

    # Prepare ticket data for Gemini API analysis
    tickets_data = []
    for ticket in all_tickets:
        tickets_data.append({
            "ticket_id": ticket.ticket_id,
            "user_id": ticket.user_id,
            "category_id": ticket.category_id,
            "title": ticket.title,
            "description": ticket.description
        })

    # Get Gemini API key from environment variable
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    # Prepare prompt for Gemini API
    prompt = f"""
    Analyze these IT support tickets and identify tickets where the title, category_id, and user_id 
    show meaningful patterns or matches. Return only the ticket_ids of tickets that have matching 
    patterns across these three fields.

    Tickets data: {json.dumps(tickets_data, indent=2)}

    Return your response as a JSON array of ticket_ids that match the criteria, like: [1, 2, 3]
    Only return the array, no additional text.
    """

    try:
        # Call Gemini API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={gemini_api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Gemini API request failed")

            # Parse Gemini response
            gemini_response = response.json()
            if "candidates" not in gemini_response or not gemini_response["candidates"]:
                raise HTTPException(status_code=500, detail="Invalid response from Gemini API")

            # Extract the text response
            response_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
            
            # Parse the JSON array of ticket_ids
            try:
                matching_ticket_ids = json.loads(response_text.strip())
                if not isinstance(matching_ticket_ids, list):
                    matching_ticket_ids = [matching_ticket_ids]
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Failed to parse Gemini API response")

        # Fetch the actual ticket objects for the matching IDs
        if matching_ticket_ids:
            query = select(Ticket).where(Ticket.ticket_id.in_(matching_ticket_ids))
            result = await db.execute(query)
            matching_tickets = result.scalars().all()
        else:
            matching_tickets = []

        return matching_tickets

    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="Failed to connect to Gemini API")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Gemini API response: {str(e)}")
