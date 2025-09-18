"""
API endpoints for ESG chatbot functionality
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from pydantic import BaseModel

from app.database import get_db
from app.models import ChatSession, ChatMessage, UserESGData, User
from app.services.chatbot_service import chatbot_service
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class UserESGDataRequest(BaseModel):
    company_name: str
    year: int
    scope1_emissions: Optional[float] = None
    scope2_emissions: Optional[float] = None
    scope3_emissions: Optional[float] = None
    water_consumption: Optional[float] = None
    waste_generated: Optional[float] = None
    energy_consumption: Optional[float] = None
    renewable_energy_percentage: Optional[float] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    additional_metrics: Optional[Dict] = None


class UserESGDataResponse(BaseModel):
    id: int
    company_name: str
    year: int
    scope1_emissions: Optional[float]
    scope2_emissions: Optional[float]
    scope3_emissions: Optional[float]
    water_consumption: Optional[float]
    waste_generated: Optional[float]
    energy_consumption: Optional[float]
    renewable_energy_percentage: Optional[float]
    employee_count: Optional[int]
    revenue: Optional[float]
    additional_metrics: Optional[Dict]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ChatSessionRequest(BaseModel):
    session_name: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: int
    session_name: str
    created_at: str
    updated_at: str
    last_message_preview: Optional[str]


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    metadata: Optional[Dict]
    created_at: str


class ESGAnalysisResponse(BaseModel):
    company_name: str
    year: int
    metrics_analysis: Dict
    overall_score: float
    recommendations: List[str]


@router.post("/esg-data", response_model=UserESGDataResponse)
async def create_or_update_esg_data(
    esg_data: UserESGDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update user's ESG data"""
    
    # Check if data already exists for this user and year
    existing_data = db.query(UserESGData).filter(
        UserESGData.user_id == current_user.id,
        UserESGData.year == esg_data.year
    ).first()
    
    if existing_data:
        # Update existing data
        for field, value in esg_data.dict(exclude_unset=True).items():
            setattr(existing_data, field, value)
        db.commit()
        db.refresh(existing_data)
        result = existing_data
    else:
        # Create new data
        new_data = UserESGData(
            user_id=current_user.id,
            **esg_data.dict()
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        result = new_data
    
    return UserESGDataResponse(
        id=result.id,
        company_name=result.company_name,
        year=result.year,
        scope1_emissions=result.scope1_emissions,
        scope2_emissions=result.scope2_emissions,
        scope3_emissions=result.scope3_emissions,
        water_consumption=result.water_consumption,
        waste_generated=result.waste_generated,
        energy_consumption=result.energy_consumption,
        renewable_energy_percentage=result.renewable_energy_percentage,
        employee_count=result.employee_count,
        revenue=result.revenue,
        additional_metrics=result.additional_metrics,
        created_at=result.created_at.isoformat(),
        updated_at=result.updated_at.isoformat()
    )


@router.get("/esg-data", response_model=List[UserESGDataResponse])
async def get_user_esg_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all ESG data for the current user"""
    
    esg_data_list = db.query(UserESGData).filter(
        UserESGData.user_id == current_user.id
    ).order_by(UserESGData.year.desc()).all()
    
    return [
        UserESGDataResponse(
            id=data.id,
            company_name=data.company_name,
            year=data.year,
            scope1_emissions=data.scope1_emissions,
            scope2_emissions=data.scope2_emissions,
            scope3_emissions=data.scope3_emissions,
            water_consumption=data.water_consumption,
            waste_generated=data.waste_generated,
            energy_consumption=data.energy_consumption,
            renewable_energy_percentage=data.renewable_energy_percentage,
            employee_count=data.employee_count,
            revenue=data.revenue,
            additional_metrics=data.additional_metrics,
            created_at=data.created_at.isoformat(),
            updated_at=data.updated_at.isoformat()
        )
        for data in esg_data_list
    ]


@router.get("/esg-data/{year}", response_model=UserESGDataResponse)
async def get_esg_data_by_year(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ESG data for a specific year"""
    
    esg_data = db.query(UserESGData).filter(
        UserESGData.user_id == current_user.id,
        UserESGData.year == year
    ).first()
    
    if not esg_data:
        raise HTTPException(status_code=404, detail=f"No ESG data found for year {year}")
    
    return UserESGDataResponse(
        id=esg_data.id,
        company_name=esg_data.company_name,
        year=esg_data.year,
        scope1_emissions=esg_data.scope1_emissions,
        scope2_emissions=esg_data.scope2_emissions,
        scope3_emissions=esg_data.scope3_emissions,
        water_consumption=esg_data.water_consumption,
        waste_generated=esg_data.waste_generated,
        energy_consumption=esg_data.energy_consumption,
        renewable_energy_percentage=esg_data.renewable_energy_percentage,
        employee_count=esg_data.employee_count,
        revenue=esg_data.revenue,
        additional_metrics=esg_data.additional_metrics,
        created_at=esg_data.created_at.isoformat(),
        updated_at=esg_data.updated_at.isoformat()
    )


@router.get("/analysis", response_model=ESGAnalysisResponse)
async def get_esg_analysis(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ESG performance analysis for user's data"""
    
    # Get user's ESG data
    if year:
        user_esg_data = db.query(UserESGData).filter(
            UserESGData.user_id == current_user.id,
            UserESGData.year == year
        ).first()
    else:
        user_esg_data = await chatbot_service.get_user_esg_data(current_user.id, db)
    
    if not user_esg_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No ESG data found{f' for year {year}' if year else ''}"
        )
    
    # Generate analysis
    analysis = await chatbot_service.analyze_user_performance(user_esg_data, db)
    
    return ESGAnalysisResponse(**analysis)


@router.post("/chat/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_request: ChatSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    
    session = await chatbot_service.create_chat_session(
        current_user.id, 
        session_request.session_name,
        db
    )
    
    return ChatSessionResponse(
        id=session.id,
        session_name=session.session_name,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        last_message_preview=None
    )


@router.get("/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chat sessions for the current user"""
    
    sessions = await chatbot_service.get_chat_sessions(current_user.id, db)
    
    return [ChatSessionResponse(**session) for session in sessions]


@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat history for a specific session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = await chatbot_service.get_chat_history(session_id, db)
    
    return [ChatMessageResponse(**message) for message in messages]


@router.post("/chat/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: int,
    message_request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to the chatbot"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    try:
        response = await chatbot_service.process_chat_message(
            session_id,
            message_request.message,
            db
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Delete all messages in the session
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    
    # Delete the session
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}


@router.get("/benchmarks/{metric}")
async def get_industry_benchmarks(
    metric: str,
    year: int = 2023,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get industry benchmarks for a specific ESG metric"""
    
    valid_metrics = [
        'scope1_emissions', 'scope2_emissions', 'scope3_emissions',
        'water_consumption', 'waste_generated', 'energy_consumption',
        'renewable_energy_percentage'
    ]
    
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Must be one of: {', '.join(valid_metrics)}"
        )
    
    benchmarks = await chatbot_service.get_industry_benchmarks(metric, year, db)
    
    if not benchmarks:
        raise HTTPException(
            status_code=404,
            detail=f"No benchmark data found for {metric} in {year}"
        )
    
    return benchmarks


@router.get("/quick-analysis")
async def get_quick_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a quick ESG analysis summary"""
    
    user_esg_data = await chatbot_service.get_user_esg_data(current_user.id, db)
    
    if not user_esg_data:
        return {
            "message": "No ESG data found. Please input your company's ESG metrics to get started with the analysis.",
            "has_data": False
        }
    
    analysis = await chatbot_service.analyze_user_performance(user_esg_data, db)
    
    # Create a summary
    summary = {
        "has_data": True,
        "company_name": analysis["company_name"],
        "year": analysis["year"],
        "overall_score": analysis["overall_score"],
        "performance_level": "Excellent" if analysis["overall_score"] >= 80 else 
                           "Good" if analysis["overall_score"] >= 60 else
                           "Average" if analysis["overall_score"] >= 40 else "Needs Improvement",
        "metrics_count": len(analysis["metrics_analysis"]),
        "top_recommendations": analysis["recommendations"][:3],
        "best_performing_metrics": [],
        "improvement_needed_metrics": []
    }
    
    # Identify best and worst performing metrics
    for metric, data in analysis["metrics_analysis"].items():
        if data["performance_level"] in ["Excellent", "Good"]:
            summary["best_performing_metrics"].append({
                "metric": metric,
                "performance": data["performance_level"],
                "percentile": data["percentile"]
            })
        elif data["performance_level"] == "Needs Improvement":
            summary["improvement_needed_metrics"].append({
                "metric": metric,
                "performance": data["performance_level"],
                "percentile": data["percentile"]
            })
    
    return summary
