from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models import Organization, User
from app.schemas import (
    Organization as OrganizationSchema,
    OrganizationCreate,
    OrganizationUpdate
)
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[OrganizationSchema])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sector: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of organizations with optional filtering"""
    try:
        query = db.query(Organization)
        
        # Apply filters
        if sector:
            query = query.filter(Organization.sector.ilike(f"%{sector}%"))
        
        if country:
            query = query.filter(Organization.country.ilike(f"%{country}%"))
        
        if search:
            query = query.filter(
                Organization.name.ilike(f"%{search}%") |
                Organization.ticker.ilike(f"%{search}%")
            )
        
        organizations = query.offset(skip).limit(limit).all()
        return organizations
        
    except Exception as e:
        logger.error(f"Failed to get organizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve organizations"
        )


@router.get("/{organization_id}", response_model=OrganizationSchema)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization by ID"""
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization


@router.post("/", response_model=OrganizationSchema)
async def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organization"""
    try:
        # Check if organization with same name already exists
        existing = db.query(Organization).filter(Organization.name == organization.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this name already exists"
            )
        
        db_organization = Organization(**organization.dict())
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        
        logger.info(f"Created organization: {db_organization.name} (ID: {db_organization.id})")
        return db_organization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create organization: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )


@router.put("/{organization_id}", response_model=OrganizationSchema)
async def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an organization"""
    try:
        db_organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Update fields that are provided
        update_data = organization_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_organization, field, value)
        
        db.commit()
        db.refresh(db_organization)
        
        logger.info(f"Updated organization: {db_organization.name} (ID: {db_organization.id})")
        return db_organization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update organization: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization"
        )


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an organization"""
    try:
        db_organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Check if organization has associated data
        from app.models import Report, KPIValue
        
        reports_count = db.query(Report).filter(Report.organization_id == organization_id).count()
        kpi_values_count = db.query(KPIValue).filter(KPIValue.organization_id == organization_id).count()
        
        if reports_count > 0 or kpi_values_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete organization with associated data ({reports_count} reports, {kpi_values_count} KPI values)"
            )
        
        db.delete(db_organization)
        db.commit()
        
        logger.info(f"Deleted organization: {db_organization.name} (ID: {organization_id})")
        return {"message": "Organization deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete organization: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete organization"
        )


@router.get("/{organization_id}/stats")
async def get_organization_stats(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for an organization"""
    try:
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        from app.models import Report, KPIValue, Recommendation
        
        # Get statistics
        reports_count = db.query(Report).filter(Report.organization_id == organization_id).count()
        kpi_values_count = db.query(KPIValue).filter(KPIValue.organization_id == organization_id).count()
        recommendations_count = db.query(Recommendation).filter(Recommendation.organization_id == organization_id).count()
        
        # Get latest report year
        latest_report = db.query(Report).filter(Report.organization_id == organization_id).order_by(Report.year.desc()).first()
        latest_year = latest_report.year if latest_report else None
        
        # Get unique KPI count
        unique_kpis = db.query(KPIValue.kpi_id).filter(KPIValue.organization_id == organization_id).distinct().count()
        
        return {
            "organization_id": organization_id,
            "organization_name": organization.name,
            "reports_count": reports_count,
            "kpi_values_count": kpi_values_count,
            "unique_kpis_count": unique_kpis,
            "recommendations_count": recommendations_count,
            "latest_report_year": latest_year,
            "data_completeness": {
                "has_reports": reports_count > 0,
                "has_kpi_data": kpi_values_count > 0,
                "has_recommendations": recommendations_count > 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve organization statistics"
        )
