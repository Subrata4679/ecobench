from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models import KPIDefinition, KPIValue, Organization, User
from app.schemas import (
    KPIDefinition as KPIDefinitionSchema,
    KPIDefinitionCreate,
    KPIValue as KPIValueSchema,
    KPIValueCreate
)
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[KPIDefinitionSchema])
async def get_kpi_definitions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of KPI definitions with optional filtering"""
    try:
        query = db.query(KPIDefinition)
        
        # Apply filters
        if category:
            query = query.filter(KPIDefinition.category.ilike(f"%{category}%"))
        
        if search:
            query = query.filter(
                KPIDefinition.name.ilike(f"%{search}%") |
                KPIDefinition.code.ilike(f"%{search}%") |
                KPIDefinition.description.ilike(f"%{search}%")
            )
        
        kpi_definitions = query.offset(skip).limit(limit).all()
        return kpi_definitions
        
    except Exception as e:
        logger.error(f"Failed to get KPI definitions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI definitions"
        )


@router.get("/{kpi_id}", response_model=KPIDefinitionSchema)
async def get_kpi_definition(
    kpi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KPI definition by ID"""
    kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_id).first()
    
    if not kpi_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI definition not found"
        )
    
    return kpi_def


@router.post("/", response_model=KPIDefinitionSchema)
async def create_kpi_definition(
    kpi_def: KPIDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new KPI definition"""
    try:
        # Check if KPI with same code already exists
        existing = db.query(KPIDefinition).filter(KPIDefinition.code == kpi_def.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="KPI with this code already exists"
            )
        
        db_kpi_def = KPIDefinition(**kpi_def.dict())
        db.add(db_kpi_def)
        db.commit()
        db.refresh(db_kpi_def)
        
        logger.info(f"Created KPI definition: {db_kpi_def.code} (ID: {db_kpi_def.id})")
        return db_kpi_def
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create KPI definition: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create KPI definition"
        )


@router.get("/values/", response_model=List[KPIValueSchema])
async def get_kpi_values(
    organization_id: Optional[int] = Query(None),
    kpi_id: Optional[int] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KPI values with optional filtering"""
    try:
        query = db.query(KPIValue)
        
        # Apply filters
        if organization_id:
            query = query.filter(KPIValue.organization_id == organization_id)
        
        if kpi_id:
            query = query.filter(KPIValue.kpi_id == kpi_id)
        
        if year_from:
            query = query.filter(KPIValue.year >= year_from)
        
        if year_to:
            query = query.filter(KPIValue.year <= year_to)
        
        kpi_values = query.order_by(KPIValue.year.desc()).offset(skip).limit(limit).all()
        return kpi_values
        
    except Exception as e:
        logger.error(f"Failed to get KPI values: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI values"
        )


@router.post("/values/", response_model=KPIValueSchema)
async def create_kpi_value(
    kpi_value: KPIValueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new KPI value"""
    try:
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == kpi_value.organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Verify KPI definition exists
        kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_value.kpi_id).first()
        if not kpi_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI definition not found"
            )
        
        db_kpi_value = KPIValue(**kpi_value.dict())
        db.add(db_kpi_value)
        db.commit()
        db.refresh(db_kpi_value)
        
        logger.info(f"Created KPI value: {kpi_def.code} for org {organization.name} (ID: {db_kpi_value.id})")
        return db_kpi_value
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create KPI value: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create KPI value"
        )


@router.get("/categories")
async def get_kpi_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of unique KPI categories"""
    try:
        categories = db.query(KPIDefinition.category).distinct().filter(
            KPIDefinition.category.isnot(None)
        ).all()
        
        return {
            "categories": [cat[0] for cat in categories if cat[0]]
        }
        
    except Exception as e:
        logger.error(f"Failed to get KPI categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI categories"
        )


@router.get("/{kpi_id}/values", response_model=List[KPIValueSchema])
async def get_kpi_values_for_kpi(
    kpi_id: int,
    organization_id: Optional[int] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all values for a specific KPI"""
    try:
        # Verify KPI exists
        kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_id).first()
        if not kpi_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI definition not found"
            )
        
        query = db.query(KPIValue).filter(KPIValue.kpi_id == kpi_id)
        
        # Apply filters
        if organization_id:
            query = query.filter(KPIValue.organization_id == organization_id)
        
        if year_from:
            query = query.filter(KPIValue.year >= year_from)
        
        if year_to:
            query = query.filter(KPIValue.year <= year_to)
        
        kpi_values = query.order_by(KPIValue.year.desc()).all()
        return kpi_values
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get KPI values for KPI {kpi_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI values"
        )


@router.get("/{kpi_id}/stats")
async def get_kpi_statistics(
    kpi_id: int,
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a KPI across all organizations"""
    try:
        # Verify KPI exists
        kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == kpi_id).first()
        if not kpi_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI definition not found"
            )
        
        query = db.query(KPIValue).filter(
            KPIValue.kpi_id == kpi_id,
            KPIValue.value_numeric.isnot(None)
        )
        
        if year:
            query = query.filter(KPIValue.year == year)
        
        kpi_values = query.all()
        
        if not kpi_values:
            return {
                "kpi_id": kpi_id,
                "kpi_code": kpi_def.code,
                "kpi_name": kpi_def.name,
                "year": year,
                "count": 0,
                "statistics": None
            }
        
        values = [kv.value_numeric for kv in kpi_values if kv.value_numeric is not None]
        
        if values:
            import statistics as stats
            
            statistics_data = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": stats.mean(values),
                "median": stats.median(values)
            }
            
            if len(values) >= 4:
                quantiles = stats.quantiles(values, n=4)
                statistics_data.update({
                    "q1": quantiles[0],
                    "q3": quantiles[2]
                })
            
            if len(values) > 1:
                statistics_data["std_dev"] = stats.stdev(values)
        else:
            statistics_data = None
        
        return {
            "kpi_id": kpi_id,
            "kpi_code": kpi_def.code,
            "kpi_name": kpi_def.name,
            "unit": kpi_def.unit,
            "year": year,
            "count": len(values),
            "statistics": statistics_data,
            "organizations_count": len(set(kv.organization_id for kv in kpi_values))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get KPI statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI statistics"
        )


@router.delete("/values/{kpi_value_id}")
async def delete_kpi_value(
    kpi_value_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a KPI value"""
    try:
        kpi_value = db.query(KPIValue).filter(KPIValue.id == kpi_value_id).first()
        
        if not kpi_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI value not found"
            )
        
        db.delete(kpi_value)
        db.commit()
        
        logger.info(f"Deleted KPI value {kpi_value_id}")
        return {"message": "KPI value deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete KPI value: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete KPI value"
        )
