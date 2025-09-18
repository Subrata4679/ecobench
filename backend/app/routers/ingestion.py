from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import asyncio

from app.database import get_db
from app.models import IngestionJob, User
from app.schemas import (
    IngestionJob as IngestionJobSchema,
    IngestionJobCreate
)
from app.routers.auth import get_current_user
from app.services.ingestion import get_ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/jobs", response_model=List[IngestionJobSchema])
async def get_ingestion_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of ingestion jobs"""
    try:
        query = db.query(IngestionJob)
        
        if status_filter:
            query = query.filter(IngestionJob.status == status_filter)
        
        jobs = query.order_by(IngestionJob.id.desc()).offset(skip).limit(limit).all()
        return jobs
        
    except Exception as e:
        logger.error(f"Failed to get ingestion jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ingestion jobs"
        )


@router.get("/jobs/{job_id}", response_model=IngestionJobSchema)
async def get_ingestion_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ingestion job by ID"""
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion job not found"
        )
    
    return job


@router.post("/jobs", response_model=IngestionJobSchema)
async def create_ingestion_job(
    job_data: IngestionJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new ingestion job"""
    try:
        ingestion_service = get_ingestion_service()
        job = await ingestion_service.create_ingestion_job(db, job_data)
        
        # Add background task to run the job
        background_tasks.add_task(run_ingestion_job_background, job.id)
        
        logger.info(f"Created ingestion job {job.id} of type {job.kind}")
        return job
        
    except Exception as e:
        logger.error(f"Failed to create ingestion job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ingestion job"
        )


@router.post("/jobs/{job_id}/run")
async def run_ingestion_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually run an ingestion job"""
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingestion job not found"
            )
        
        if job.status not in ["pending", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job cannot be run in current status: {job.status}"
            )
        
        # Reset job status
        job.status = "pending"
        db.commit()
        
        # Add background task to run the job
        background_tasks.add_task(run_ingestion_job_background, job_id)
        
        return {"message": f"Job {job_id} queued for execution"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run ingestion job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run ingestion job"
        )


@router.delete("/jobs/{job_id}")
async def delete_ingestion_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an ingestion job"""
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingestion job not found"
            )
        
        if job.status == "running":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a running job"
            )
        
        db.delete(job)
        db.commit()
        
        logger.info(f"Deleted ingestion job {job_id}")
        return {"message": "Ingestion job deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete ingestion job: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete ingestion job"
        )


@router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed status of an ingestion job"""
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingestion job not found"
            )
        
        # Calculate progress based on job type and status
        progress = 0
        if job.status == "completed":
            progress = 100
        elif job.status == "running":
            # Estimate progress based on job type
            if job.kind == "pdf_upload":
                progress = 50  # Assume halfway through
            elif job.kind == "url_fetch":
                progress = 30
            elif job.kind == "extraction":
                progress = 70
        elif job.status == "failed":
            progress = 0
        
        return {
            "job_id": job.id,
            "status": job.status,
            "kind": job.kind,
            "progress": progress,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "logs": job.logs,
            "params": job.params
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status"
        )


async def run_ingestion_job_background(job_id: int):
    """Background task to run an ingestion job"""
    try:
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            ingestion_service = get_ingestion_service()
            result = await ingestion_service.run_job(db, job_id)
            
            if result["success"]:
                logger.info(f"Ingestion job {job_id} completed successfully")
            else:
                logger.error(f"Ingestion job {job_id} failed: {result.get('error')}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Background job execution failed for job {job_id}: {e}")


@router.post("/extract/{report_id}")
async def extract_kpis_from_report(
    report_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create extraction job for a specific report"""
    try:
        from app.models import Report
        
        # Verify report exists
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Create extraction job
        ingestion_service = get_ingestion_service()
        job_data = IngestionJobCreate(
            kind="extraction",
            params={"report_id": report_id}
        )
        
        job = await ingestion_service.create_ingestion_job(db, job_data)
        
        # Add background task to run the job
        background_tasks.add_task(run_ingestion_job_background, job.id)
        
        return {
            "message": f"Extraction job created for report {report_id}",
            "job_id": job.id,
            "report_id": report_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create extraction job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create extraction job"
        )
