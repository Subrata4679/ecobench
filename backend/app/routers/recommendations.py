from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models import Recommendation, User
from app.schemas import (
    Recommendation as RecommendationSchema,
    RecommendationCreate
)
from app.routers.auth import get_current_user
from app.services.guidance import get_guidance_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[RecommendationSchema])
async def get_recommendations(
    organization_id: Optional[int] = Query(None),
    kpi_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of recommendations with optional filtering"""
    try:
        query = db.query(Recommendation)
        
        # Apply filters
        if organization_id:
            query = query.filter(Recommendation.organization_id == organization_id)
        
        if kpi_id:
            query = query.filter(Recommendation.kpi_id == kpi_id)
        
        recommendations = query.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations"
        )


@router.get("/{recommendation_id}", response_model=RecommendationSchema)
async def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recommendation by ID"""
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation


@router.post("/generate")
async def generate_recommendation(
    organization_id: int,
    kpi_id: int,
    period: str = "2023",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered recommendation for an organization's KPI"""
    try:
        guidance_service = get_guidance_service()
        
        # Generate guidance
        result = await guidance_service.generate_kpi_guidance(
            db, organization_id, kpi_id, period
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        guidance = result["guidance"]
        
        # Save recommendation to database
        recommendation_data = {
            "organization_id": organization_id,
            "kpi_id": kpi_id,
            "title": guidance.get("title", "AI-Generated Recommendation"),
            "rationale": guidance.get("rationale"),
            "actions": guidance.get("actions", []),
            "confidence": guidance.get("confidence"),
            "sources": guidance.get("sources", [])
        }
        
        recommendation = await guidance_service.save_recommendation(db, recommendation_data)
        
        return {
            "message": "Recommendation generated successfully",
            "recommendation_id": recommendation.id,
            "guidance": guidance,
            "context": result.get("context", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendation"
        )


@router.post("/comprehensive")
async def generate_comprehensive_guidance(
    organization_id: int,
    period: str = "2023",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive guidance across all KPIs for an organization"""
    try:
        guidance_service = get_guidance_service()
        
        result = await guidance_service.generate_comprehensive_guidance(
            db, organization_id, period
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result["comprehensive_report"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate comprehensive guidance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate comprehensive guidance"
        )


@router.post("/", response_model=RecommendationSchema)
async def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recommendation manually"""
    try:
        from app.models import Organization, KPIDefinition
        
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == recommendation.organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Verify KPI exists if specified
        if recommendation.kpi_id:
            kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == recommendation.kpi_id).first()
            if not kpi_def:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="KPI definition not found"
                )
        
        db_recommendation = Recommendation(**recommendation.dict())
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        
        logger.info(f"Created recommendation: {db_recommendation.title} (ID: {db_recommendation.id})")
        return db_recommendation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create recommendation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recommendation"
        )


@router.put("/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: int,
    status: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the implementation status of a recommendation"""
    try:
        guidance_service = get_guidance_service()
        
        success = await guidance_service.update_recommendation_status(
            db, recommendation_id, status, notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        return {
            "message": "Recommendation status updated successfully",
            "recommendation_id": recommendation_id,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update recommendation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recommendation status"
        )


@router.delete("/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recommendation"""
    try:
        recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        db.delete(recommendation)
        db.commit()
        
        logger.info(f"Deleted recommendation {recommendation_id}")
        return {"message": "Recommendation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete recommendation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recommendation"
        )


@router.get("/organization/{organization_id}/summary")
async def get_organization_recommendations_summary(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary of recommendations for an organization"""
    try:
        from app.models import Organization
        
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get recommendations
        recommendations = db.query(Recommendation).filter(
            Recommendation.organization_id == organization_id
        ).order_by(Recommendation.created_at.desc()).all()
        
        # Calculate summary statistics
        total_recommendations = len(recommendations)
        high_confidence = sum(1 for r in recommendations if r.confidence and r.confidence > 0.8)
        
        # Group by KPI
        kpi_breakdown = {}
        for rec in recommendations:
            if rec.kpi_id:
                if rec.kpi_id not in kpi_breakdown:
                    kpi_breakdown[rec.kpi_id] = 0
                kpi_breakdown[rec.kpi_id] += 1
        
        # Get recent recommendations (last 5)
        recent_recommendations = recommendations[:5]
        
        return {
            "organization_id": organization_id,
            "organization_name": organization.name,
            "summary": {
                "total_recommendations": total_recommendations,
                "high_confidence_recommendations": high_confidence,
                "kpi_breakdown": kpi_breakdown,
                "recent_count": len(recent_recommendations)
            },
            "recent_recommendations": [
                {
                    "id": rec.id,
                    "title": rec.title,
                    "kpi_id": rec.kpi_id,
                    "confidence": rec.confidence,
                    "created_at": rec.created_at
                }
                for rec in recent_recommendations
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recommendations summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations summary"
        )
