from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from typing import Dict, Any, Optional, List
import os
import json
import httpx
import logging
from db import get_db
from dotenv import load_dotenv
from pydantic import BaseModel
from models.chatbot_models import ChatbotConversation, ChatbotConversationOut, ChatbotConversationSummary
from models.ticketModels import User
from datetime import datetime, timedelta
import asyncio

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ChatbotRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str
    confidence: str
    recommendation: Optional[str] = None

class WeeklyReportData(BaseModel):
    total_conversations: int
    new_conversations: int
    top_issues: List[Dict[str, Any]]
    user_activity: Dict[str, int]
    confidence_distribution: Dict[str, int]
    ai_insights: str
    recommendations: List[str]
    report_period: str

# Global variable to store the scheduler task
scheduler_task = None

async def send_weekly_report_to_it_hod():
    """
    Background task to send weekly chatbot summary report to IT HOD users.
    Runs every Monday at 12 AM.
    """
    try:
        logger.info("🕐 Starting weekly chatbot report generation...")
        
        # Get database session
        from db import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            # Get IT HOD users (role = "IT HOD" and department = "administration")
            it_hod_query = select(User).where(
                User.role == "IT HOD",
                User.department == "administration"
            )
            result = await db.execute(it_hod_query)
            it_hod_users = result.scalars().all()
            
            if not it_hod_users:
                logger.warning("No IT HOD users found for weekly report")
                return
            
            logger.info(f"📧 Sending weekly report to {len(it_hod_users)} IT HOD users")
            
            # Generate AI-powered summary
            weekly_summary = await generate_ai_weekly_summary(db)
            
            # Send report to each IT HOD user
            for user in it_hod_users:
                await send_report_to_user(user, weekly_summary)
                
        logger.info("✅ Weekly chatbot report sent successfully")
        
    except Exception as e:
        logger.error(f"❌ Error sending weekly report: {str(e)}")

async def generate_ai_weekly_summary(db: AsyncSession) -> WeeklyReportData:
    """
    Generate AI-powered weekly summary using Gemini API.
    """
    try:
        # Get conversation data for the past week
        week_ago = datetime.now() - timedelta(days=7)
        
        # Total conversations this week
        weekly_total_query = select(func.count(ChatbotConversation.conversation_id)).where(
            ChatbotConversation.created_at >= week_ago
        )
        weekly_total_result = await db.execute(weekly_total_query)
        weekly_total = weekly_total_result.scalar()
        
        # New conversations (compared to previous week)
        two_weeks_ago = datetime.now() - timedelta(days=14)
        previous_week_query = select(func.count(ChatbotConversation.conversation_id)).where(
            ChatbotConversation.created_at >= two_weeks_ago,
            ChatbotConversation.created_at < week_ago
        )
        previous_week_result = await db.execute(previous_week_query)
        previous_week_total = previous_week_result.scalar()
        new_conversations = weekly_total - previous_week_total
        
        # Top issues by frequency
        top_issues_query = select(
            ChatbotConversation.message,
            func.count(ChatbotConversation.conversation_id).label('count')
        ).where(
            ChatbotConversation.created_at >= week_ago
        ).group_by(
            ChatbotConversation.message
        ).order_by(
            desc(func.count(ChatbotConversation.conversation_id))
        ).limit(10)
        
        top_issues_result = await db.execute(top_issues_query)
        top_issues = [
            {"issue": row[0], "frequency": row[1]} 
            for row in top_issues_result.fetchall()
        ]
        
        # User activity
        user_activity_query = select(
            ChatbotConversation.user_id,
            func.count(ChatbotConversation.conversation_id).label('count')
        ).where(
            ChatbotConversation.created_at >= week_ago,
            ChatbotConversation.user_id.isnot(None)
        ).group_by(
            ChatbotConversation.user_id
        )
        
        user_activity_result = await db.execute(user_activity_query)
        user_activity = {
            str(row[0]): row[1] 
            for row in user_activity_result.fetchall()
        }
        
        # Confidence distribution
        confidence_query = select(
            ChatbotConversation.confidence,
            func.count(ChatbotConversation.conversation_id).label('count')
        ).where(
            ChatbotConversation.created_at >= week_ago
        ).group_by(
            ChatbotConversation.confidence
        )
        
        confidence_result = await db.execute(confidence_query)
        confidence_distribution = {
            row[0]: row[1] 
            for row in confidence_result.fetchall()
        }
        
        # Generate AI insights using Gemini
        ai_insights = await generate_ai_insights(
            weekly_total, top_issues, user_activity, confidence_distribution
        )
        
        # Generate recommendations
        recommendations = await generate_recommendations(
            weekly_total, top_issues, confidence_distribution
        )
        
        return WeeklyReportData(
            total_conversations=weekly_total,
            new_conversations=new_conversations,
            top_issues=top_issues,
            user_activity=user_activity,
            confidence_distribution=confidence_distribution,
            ai_insights=ai_insights,
            recommendations=recommendations,
            report_period=f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"
        )
        
    except Exception as e:
        logger.error(f"Error generating weekly summary: {str(e)}")
        raise

async def generate_ai_insights(
    total_conversations: int,
    top_issues: List[Dict[str, Any]],
    user_activity: Dict[str, int],
    confidence_distribution: Dict[str, int]
) -> str:
    """
    Use Gemini AI to generate insights from chatbot data.
    """
    try:
        prompt = f"""
        As an IT Support Analyst, analyze this chatbot conversation data and provide 2-3 key insights:
        
        Weekly Summary Data:
        - Total conversations: {total_conversations}
        - Top issues: {json.dumps(top_issues, indent=2)}
        - User activity: {json.dumps(user_activity, indent=2)}
        - Confidence distribution: {json.dumps(confidence_distribution, indent=2)}
        
        Provide 2-3 concise, actionable insights about:
        1. What patterns you see in user issues
        2. How well the chatbot is performing
        3. What areas might need attention
        
        Keep each insight under 50 words. Be specific and actionable.
        """
        
        request_data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        request_headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": gemini_api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers=request_headers,
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                gemini_response = response.json()
                if "candidates" in gemini_response and gemini_response["candidates"]:
                    response_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
                    return response_text.strip()
            
        return "AI analysis temporarily unavailable. Please review the data manually."
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return "AI analysis failed. Please review the data manually."

async def generate_recommendations(
    total_conversations: int,
    top_issues: List[Dict[str, Any]],
    confidence_distribution: Dict[str, int]
) -> List[str]:
    """
    Generate actionable recommendations based on chatbot data.
    """
    recommendations = []
    
    try:
        # Analyze confidence levels
        low_confidence = confidence_distribution.get("low", 0)
        if low_confidence > 0:
            low_percentage = (low_confidence / total_conversations) * 100
            if low_percentage > 20:
                recommendations.append("High number of low-confidence responses. Consider updating chatbot knowledge base.")
        
        # Analyze issue patterns
        if top_issues:
            most_common = top_issues[0]
            if most_common["frequency"] > total_conversations * 0.3:
                recommendations.append(f"'{most_common['issue'][:50]}...' is very common. Consider adding to FAQ or creating a knowledge article.")
        
        # Volume recommendations
        if total_conversations > 100:
            recommendations.append("High chatbot usage suggests it's effective. Consider expanding capabilities.")
        elif total_conversations < 10:
            recommendations.append("Low chatbot usage. Consider promoting the service to users.")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Monitor chatbot performance and user satisfaction.")
            recommendations.append("Regularly update knowledge base with common issues.")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return ["Error generating recommendations. Please review data manually."]

async def send_report_to_user(user: User, report_data: WeeklyReportData):
    """
    Send weekly report to a specific IT HOD user.
    In a real implementation, this would send an email or notification.
    """
    try:
        # For now, we'll log the report. In production, implement email/notification system
        logger.info(f"📊 Weekly Report for {user.first_name} {user.last_name} ({user.email})")
        logger.info(f"   Report Period: {report_data.report_period}")
        logger.info(f"   Total Conversations: {report_data.total_conversations}")
        logger.info(f"   New Conversations: {report_data.new_conversations}")
        logger.info(f"   AI Insights: {report_data.ai_insights}")
        logger.info(f"   Recommendations: {', '.join(report_data.recommendations)}")
        
        # TODO: Implement actual email/notification sending here
        # Example: await send_email(user.email, "Weekly Chatbot Report", generate_email_content(report_data))
        
    except Exception as e:
        logger.error(f"Error sending report to user {user.user_id}: {str(e)}")

async def schedule_weekly_reports():
    """
    Schedule weekly reports to run every Monday at 12 AM.
    """
    global scheduler_task
    
    while True:
        now = datetime.now()
        
        # Calculate next Monday at 12 AM
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0 and now.hour >= 12:
            # If it's Monday and past 12 AM, schedule for next Monday
            days_until_monday = 7
        
        next_monday = now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        
        # Calculate seconds until next Monday 12 AM
        seconds_until_monday = (next_monday - now).total_seconds()
        
        logger.info(f"📅 Next weekly report scheduled for: {next_monday}")
        logger.info(f"⏰ Will run in {seconds_until_monday/3600:.1f} hours")
        
        # Wait until next Monday 12 AM
        await asyncio.sleep(seconds_until_monday)
        
        # Send the weekly report
        await send_weekly_report_to_it_hod()

@router.on_event("startup")
async def start_scheduler():
    """
    Start the weekly report scheduler when the application starts.
    """
    global scheduler_task
    if scheduler_task is None:
        scheduler_task = asyncio.create_task(schedule_weekly_reports())
        logger.info("🚀 Weekly report scheduler started")

@router.on_event("shutdown")
async def stop_scheduler():
    """
    Stop the weekly report scheduler when the application shuts down.
    """
    global scheduler_task
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        logger.info("🛑 Weekly report scheduler stopped")

@router.post("/chat", response_model=ChatbotResponse)
async def chat_with_faq_bot(
    request: ChatbotRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    IT FAQ Chatbot endpoint that provides basic troubleshooting guidance.
    Restricted to IT-related questions only. Complex issues are referred to IT support.
    All conversations are stored in the database.
    """
    
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable.")
    
    # Prepare the restricted prompt for Gemini AI
    prompt = f"""
    You are an IT Support FAQ chatbot. Your role is to provide ONLY basic troubleshooting guidance for common IT issues.
    
    IMPORTANT RESTRICTIONS:
    1. ONLY answer IT-related questions
    2. Provide ONLY simple, basic troubleshooting steps
    3. If the issue is complex, requires system access, or involves security - ALWAYS recommend contacting IT support
    4. Keep responses under 150 words
    5. Be helpful but cautious - don't give advanced technical advice
    
    ALLOWED TOPICS (basic guidance only):
    - Password resets (basic steps)
    - Printer connectivity (check cables, restart)
    - Internet connectivity (check router, restart modem)
    - Software installation (basic download/install steps)
    - Email access issues (check credentials, clear cache)
    
    RESTRICTED TOPICS (refer to IT support):
    - System administration
    - Network configuration
    - Security issues
    - Hardware repairs
    - Advanced troubleshooting
    - Any issue requiring system access
    
    User message: "{request.message}"
    
    Respond in this exact JSON format:
    {{
        "response": "Your helpful but basic troubleshooting guidance here",
        "confidence": "high/medium/low",
        "recommendation": "Contact IT support if this doesn't resolve your issue" (always include this)
    }}
    
    If the question is NOT IT-related, respond with:
    {{
        "response": "I can only help with IT-related questions. Please ask about computer, software, or network issues.",
        "confidence": "high",
        "recommendation": "Ask an IT-related question for assistance"
    }}
    
    If the issue is complex or requires advanced technical knowledge, respond with:
    {{
        "response": "This issue requires advanced technical assistance that I cannot provide safely.",
        "confidence": "high", 
        "recommendation": "Please contact IT support immediately for this issue"
    }}
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
        
        logger.info(f"Chatbot request from user {request.user_id}: {request.message}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers=request_headers,
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API request failed: {response.status_code}")
                raise HTTPException(status_code=500, detail="Chatbot service temporarily unavailable")

            # Parse Gemini response
            gemini_response = response.json()
            
            if "candidates" not in gemini_response or not gemini_response["candidates"]:
                raise HTTPException(status_code=500, detail="Invalid response from chatbot service")

            # Extract the text response
            response_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
            
            # Parse the JSON response
            try:
                # Clean the response text
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                
                cleaned_text = cleaned_text.strip()
                chatbot_response = json.loads(cleaned_text)
                
                # Validate response structure
                if not all(key in chatbot_response for key in ["response", "confidence", "recommendation"]):
                    raise ValueError("Invalid response structure")
                
                # Store the conversation in the database
                conversation = ChatbotConversation(
                    user_id=request.user_id,
                    message=request.message,
                    response=chatbot_response["response"],
                    confidence=chatbot_response["confidence"],
                    recommendation=chatbot_response["recommendation"]
                )
                
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)
                
                logger.info(f"Chatbot conversation stored in database with ID: {conversation.conversation_id}")
                logger.info(f"Chatbot response generated successfully for user {request.user_id}")
                
                return ChatbotResponse(**chatbot_response)
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse chatbot response: {str(e)}")
                # Fallback response
                fallback_response = ChatbotResponse(
                    response="I'm having trouble processing your request right now.",
                    confidence="low",
                    recommendation="Please contact IT support for immediate assistance"
                )
                
                # Store the fallback conversation
                conversation = ChatbotConversation(
                    user_id=request.user_id,
                    message=request.message,
                    response=fallback_response.response,
                    confidence=fallback_response.confidence,
                    recommendation=fallback_response.recommendation
                )
                
                db.add(conversation)
                await db.commit()
                
                return fallback_response

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Gemini API: {str(e)}")
        raise HTTPException(status_code=500, detail="Chatbot service temporarily unavailable")
        
    except Exception as e:
        logger.error(f"Unexpected error in chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/conversations", response_model=List[ChatbotConversationOut])
async def get_conversation_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve conversation history with optional filtering by user ID.
    Supports pagination with limit and offset parameters.
    """
    try:
        query = select(ChatbotConversation).order_by(desc(ChatbotConversation.created_at))
        
        if user_id:
            query = query.where(ChatbotConversation.user_id == user_id)
        
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        conversations = result.scalars().all()
        
        return conversations
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")

@router.get("/conversations/summary", response_model=WeeklyReportData)
async def get_conversation_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered summary statistics of chatbot conversations for the past week.
    This endpoint provides intelligent analysis and insights using Gemini AI.
    """
    try:
        weekly_summary = await generate_ai_weekly_summary(db)
        return weekly_summary
        
    except Exception as e:
        logger.error(f"Error retrieving conversation summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation summary")

@router.get("/conversations/{conversation_id}", response_model=ChatbotConversationOut)
async def get_conversation_by_id(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific conversation by its ID.
    """
    try:
        result = await db.execute(
            select(ChatbotConversation).where(ChatbotConversation.conversation_id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")

@router.post("/conversations/analyze", response_model=Dict[str, Any])
async def analyze_conversations(
    analysis_type: str = Query("weekly_summary", description="Type of analysis: weekly_summary, trend_analysis, issue_patterns"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI analysis of chatbot conversations.
    Supports different analysis types: weekly_summary, trend_analysis, issue_patterns
    """
    try:
        if analysis_type == "weekly_summary":
            analysis_result = await generate_ai_weekly_summary(db)
            return {
                "analysis_type": "weekly_summary",
                "status": "completed",
                "data": analysis_result.dict()
            }
        else:
            return {
                "analysis_type": analysis_type,
                "status": "not_implemented",
                "message": f"Analysis type '{analysis_type}' not yet implemented"
            }
            
    except Exception as e:
        logger.error(f"Error analyzing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze conversations")

@router.post("/reports/recover-missed", response_model=Dict[str, Any])
async def recover_missed_reports(
    background_tasks: BackgroundTasks
):
    """
    Manually trigger recovery of missed weekly reports.
    This endpoint can be used to recover reports that were missed due to server downtime.
    """
    try:
        logger.info("🔄 Manual trigger: Recovering missed weekly reports")
        
        # Add the recovery task to background tasks
        background_tasks.add_task(check_and_send_missed_reports)
        
        return {
            "status": "recovery_triggered",
            "message": "Missed report recovery has been triggered in the background",
            "note": "Check logs for recovery progress and results"
        }
        
    except Exception as e:
        logger.error(f"Error triggering missed report recovery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger report recovery")

@router.get("/reports/status", response_model=Dict[str, Any])
async def get_report_status():
    """
    Get the current status of weekly reporting system.
    """
    try:
        now = datetime.now()
        
        # Calculate next report time
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0 and now.hour >= 12:
            days_until_monday = 7
        
        next_monday = now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        seconds_until_next = (next_monday - now).total_seconds()
        
        # Check if we're in a recovery scenario
        is_monday_after_12 = now.weekday() == 0 and now.hour >= 12
        
        return {
            "scheduler_status": {
                "running": scheduler_task is not None and not scheduler_task.done(),
                "next_report": next_monday.isoformat(),
                "time_until_next": f"{seconds_until_next/3600:.1f} hours",
                "current_day": now.strftime("%A"),
                "current_time": now.strftime("%H:%M:%S")
            },
            "recovery_status": {
                "needs_recovery": is_monday_after_12,
                "last_monday": (now - timedelta(days=now.weekday())).replace(hour=12, minute=0, second=0, microsecond=0).isoformat(),
                "can_trigger_recovery": is_monday_after_12
            },
            "system_info": {
                "server_timezone": "Local server time",
                "report_frequency": "Every Monday at 12:00 AM",
                "recovery_enabled": True,
                "max_recovery_weeks": 4
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting report status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get report status")

@router.get("/health")
async def chatbot_health_check():
    """
    Health check endpoint for the chatbot service
    """
    return {
        "status": "healthy",
        "service": "IT FAQ Chatbot",
        "gemini_api_configured": bool(gemini_api_key),
        "weekly_scheduler_running": scheduler_task is not None and not scheduler_task.done(),
        "offline_recovery_enabled": True,
        "features": [
            "AI-powered conversation analysis",
            "Automated weekly reports (Mondays 12 AM)",
            "Offline recovery for missed reports",
            "Manual recovery trigger",
            "Report status monitoring"
        ]
    }

@router.get("/capabilities")
async def get_chatbot_capabilities():
    """
    Returns information about what the chatbot can and cannot help with
    """
    return {
        "service": "IT FAQ Chatbot",
        "capabilities": [
            "Basic password reset guidance",
            "Simple printer connectivity troubleshooting", 
            "Basic internet connectivity checks",
            "Simple software installation steps",
            "Basic email access troubleshooting"
        ],
        "limitations": [
            "Cannot provide advanced technical support",
            "Cannot access systems or perform repairs",
            "Cannot handle security incidents",
            "Cannot provide network configuration help",
            "Complex issues are referred to IT support"
        ],
        "recommendation": "For complex issues, always contact IT support directly",
        "ai_features": [
            "AI-powered conversation analysis",
            "Weekly automated reports for IT HOD",
            "Intelligent issue pattern recognition",
            "Automated recommendations generation"
        ]
    }
