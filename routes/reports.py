from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
import os
import json
import httpx
import logging
from db import get_db
from models.ticketModels import Ticket
from models.ticketModels import TicketOut
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")    # Get Gemini API key from environment variable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/tickets/recurring", response_model=List[TicketOut])
async def get_recurring_tickets(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches all tickets and uses Gemini 2.0 Flash API to analyze and return tickets 
    that are recurring based on matching title, category_id, and user_id patterns.
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

    # Use Gemini API key from environment variable
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable.")
    
    logger.info(f"Using Gemini API key: {gemini_api_key[:10]}...{gemini_api_key[-10:] if len(gemini_api_key) > 20 else '***'}")

    # Prepare prompt for Gemini API to detect recurring tickets
    prompt = f"""
    Analyze these IT support tickets and identify ONLY TRUE RECURRING tickets where ALL 3 conditions must match:
    1. EXACTLY the same title (or very similar titles that clearly describe the same issue)
    2. Same category_id (same type of issue)
    3. Same user_id (same person experiencing the issue)
    
    IMPORTANT: Do NOT consider tickets recurring if only category_id and user_id match but titles are completely different.
    Only mark as recurring if the titles are essentially the same problem being reported repeatedly.
    
    Examples of what IS recurring:
    - "Printer not working" and "Printer still not working" (same issue, same user, same category)
    - "Network down" and "Network still down" (same issue, same user, same category)
    
    Examples of what is NOT recurring:
    - "Printer not working" and "Network down" (different issues, even if same user/category)
    - "E22" and "G 05" (completely different titles, not recurring)
    
    Tickets data: {json.dumps(tickets_data, indent=2)}

    Return your response as a JSON array of ticket_ids that represent TRUE recurring issues, like: [1, 2, 3]
    If no true recurring tickets found, return an empty array: []
    Only return the array, no additional text.
    """

    try:
        # Call Gemini 2.0 Flash API
        request_data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        request_headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": gemini_api_key
        }
        
        logger.info(f"Sending request to Gemini API with headers: {request_headers}")
        logger.info(f"Request payload: {json.dumps(request_data, indent=2)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers=request_headers,
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API request failed with status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                logger.error(f"Response headers: {response.headers}")
                raise HTTPException(status_code=500, detail=f"Gemini API request failed: {response.status_code}. Response: {response.text}")

            # Parse Gemini response
            gemini_response = response.json()
            logger.info(f"Full Gemini API response: {gemini_response}")
            
            if "candidates" not in gemini_response or not gemini_response["candidates"]:
                logger.error("Invalid response from Gemini API: no candidates found")
                logger.error(f"Response structure: {gemini_response}")
                raise HTTPException(status_code=500, detail="Invalid response from Gemini API: no candidates found")

            # Extract the text response
            response_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
            logger.info(f"Raw response text from Gemini: {response_text}")
            
            # Parse the JSON array of ticket_ids
            try:
                # Clean the response text by removing markdown code blocks if present
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]  # Remove ```json
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]  # Remove ```
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]  # Remove ```
                
                cleaned_text = cleaned_text.strip()
                logger.info(f"Cleaned response text: '{cleaned_text}'")
                
                matching_ticket_ids = json.loads(cleaned_text)
                if not isinstance(matching_ticket_ids, list):
                    matching_ticket_ids = [matching_ticket_ids]
                logger.info(f"Matching ticket IDs from Gemini API: {matching_ticket_ids}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini API response as JSON: {str(e)}")
                logger.error(f"Response text that failed to parse: '{response_text}'")
                logger.error(f"Cleaned text that failed to parse: '{cleaned_text}'")
                raise HTTPException(status_code=500, detail=f"Failed to parse Gemini API response as JSON. Response: {response_text}")

        # Fetch the actual ticket objects for the matching IDs
        if matching_ticket_ids:
            query = select(Ticket).where(Ticket.ticket_id.in_(matching_ticket_ids))
            result = await db.execute(query)
            matching_tickets = result.scalars().all()
        else:
            matching_tickets = []

        return matching_tickets

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Gemini API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Gemini API: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error processing Gemini API response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing Gemini API response: {str(e)}")
