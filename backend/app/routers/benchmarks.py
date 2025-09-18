from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models import PeerGroup, BenchmarkSnapshot, User
from app.schemas import BenchmarkRequest, BenchmarkSnapshot as BenchmarkSnapshotSchema
from app.routers.auth import get_current_user
from app.services.benchmark import get_benchmark_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/snapshot", response_model=BenchmarkSnapshotSchema)
async def create_benchmark_snapshot(
    request: BenchmarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a benchmark snapshot for a peer group and KPI"""
    try:
        benchmark_service = get_benchmark_service()
        
        snapshot = benchmark_service.create_benchmark_snapshot(
            db, request.peer_group_id, request.kpi_id, request.period
        )
        
        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data to create benchmark snapshot"
            )
        
        return snapshot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create benchmark snapshot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create benchmark snapshot"
        )


@router.get("/organization/{organization_id}/percentile")
async def get_organization_percentile(
    organization_id: int,
    kpi_id: int = Query(...),
    period: str = Query(...),
    peer_group_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization's percentile ranking for a KPI"""
    try:
        benchmark_service = get_benchmark_service()
        
        result = benchmark_service.get_organization_percentile(
            db, organization_id, kpi_id, period, peer_group_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization percentile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get organization percentile"
        )


@router.get("/top-performers")
async def get_top_performers(
    kpi_id: int = Query(...),
    period: str = Query(...),
    peer_group_id: Optional[int] = Query(None),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top performing organizations for a KPI"""
    try:
        benchmark_service = get_benchmark_service()
        
        top_performers = benchmark_service.get_top_performers(
            db, kpi_id, period, peer_group_id, limit
        )
        
        return {
            "kpi_id": kpi_id,
            "period": period,
            "peer_group_id": peer_group_id,
            "top_performers": top_performers
        }
        
    except Exception as e:
        logger.error(f"Failed to get top performers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get top performers"
        )


@router.post("/compare")
async def compare_organizations(
    organization_ids: List[int],
    kpi_id: int,
    period: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple organizations on a specific KPI"""
    try:
        if len(organization_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 organizations required for comparison"
            )
        
        if len(organization_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 organizations allowed for comparison"
            )
        
        benchmark_service = get_benchmark_service()
        
        comparison = benchmark_service.compare_organizations(
            db, organization_ids, kpi_id, period
        )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compare organizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare organizations"
        )


@router.get("/peer-groups", response_model=List[dict])
async def get_peer_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of peer groups"""
    try:
        peer_groups = db.query(PeerGroup).offset(skip).limit(limit).all()
        
        result = []
        for pg in peer_groups:
            # Get organization count for each peer group
            benchmark_service = get_benchmark_service()
            orgs = benchmark_service.get_peer_organizations(db, pg.criteria)
            
            result.append({
                "id": pg.id,
                "name": pg.name,
                "criteria": pg.criteria,
                "organization_count": len(orgs)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get peer groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve peer groups"
        )


@router.post("/peer-groups")
async def create_peer_group(
    name: str,
    criteria: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new peer group"""
    try:
        benchmark_service = get_benchmark_service()
        
        peer_group = benchmark_service.create_peer_group(db, name, criteria)
        
        # Get organization count
        orgs = benchmark_service.get_peer_organizations(db, criteria)
        
        return {
            "id": peer_group.id,
            "name": peer_group.name,
            "criteria": peer_group.criteria,
            "organization_count": len(orgs),
            "organizations": [{"id": org.id, "name": org.name} for org in orgs[:10]]  # First 10
        }
        
    except Exception as e:
        logger.error(f"Failed to create peer group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create peer group"
        )


@router.get("/peer-groups/{peer_group_id}")
async def get_peer_group(
    peer_group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get peer group details"""
    try:
        peer_group = db.query(PeerGroup).filter(PeerGroup.id == peer_group_id).first()
        
        if not peer_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer group not found"
            )
        
        benchmark_service = get_benchmark_service()
        orgs = benchmark_service.get_peer_organizations(db, peer_group.criteria)
        
        return {
            "id": peer_group.id,
            "name": peer_group.name,
            "criteria": peer_group.criteria,
            "organization_count": len(orgs),
            "organizations": [
                {
                    "id": org.id,
                    "name": org.name,
                    "sector": org.sector,
                    "country": org.country
                }
                for org in orgs
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get peer group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get peer group"
        )


@router.get("/snapshots")
async def get_benchmark_snapshots(
    peer_group_id: Optional[int] = Query(None),
    kpi_id: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get benchmark snapshots with optional filtering"""
    try:
        query = db.query(BenchmarkSnapshot)
        
        if peer_group_id:
            query = query.filter(BenchmarkSnapshot.peer_group_id == peer_group_id)
        
        if kpi_id:
            query = query.filter(BenchmarkSnapshot.kpi_id == kpi_id)
        
        if period:
            query = query.filter(BenchmarkSnapshot.period == period)
        
        snapshots = query.order_by(BenchmarkSnapshot.created_at.desc()).offset(skip).limit(limit).all()
        
        return snapshots
        
    except Exception as e:
        logger.error(f"Failed to get benchmark snapshots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve benchmark snapshots"
        )


@router.delete("/peer-groups/{peer_group_id}")
async def delete_peer_group(
    peer_group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a peer group"""
    try:
        peer_group = db.query(PeerGroup).filter(PeerGroup.id == peer_group_id).first()
        
        if not peer_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer group not found"
            )
        
        # Check if peer group has associated snapshots
        snapshots_count = db.query(BenchmarkSnapshot).filter(
            BenchmarkSnapshot.peer_group_id == peer_group_id
        ).count()
        
        if snapshots_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete peer group with {snapshots_count} associated benchmark snapshots"
            )
        
        db.delete(peer_group)
        db.commit()
        
        logger.info(f"Deleted peer group: {peer_group.name} (ID: {peer_group_id})")
        return {"message": "Peer group deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete peer group: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete peer group"
        )
