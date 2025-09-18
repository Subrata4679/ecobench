from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import aiofiles
import os

from app.database import get_db
from app.models import Report, Organization, User
from app.schemas import (
    Report as ReportSchema,
    ReportCreate,
    ReportUpdate,
    FileUploadResponse
)
from app.routers.auth import get_current_user
from app.services.ingestion import get_ingestion_service
from app.utils.pdf_utils import PDFProcessor
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ReportSchema])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of reports with optional filtering"""
    try:
        query = db.query(Report)
        
        # Apply filters
        if organization_id:
            query = query.filter(Report.organization_id == organization_id)
        
        if year:
            query = query.filter(Report.year == year)
        
        if status:
            query = query.filter(Report.status == status)
        
        reports = query.offset(skip).limit(limit).all()
        return reports
        
    except Exception as e:
        logger.error(f"Failed to get reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports"
        )


@router.get("/{report_id}", response_model=ReportSchema)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@router.post("/", response_model=ReportSchema)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new report"""
    try:
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == report.organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        db_report = Report(**report.dict())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        logger.info(f"Created report: {db_report.title} (ID: {db_report.id})")
        return db_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create report: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_report(
    organization_id: int = Form(...),
    title: str = Form(...),
    year: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF report file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Save file
        pdf_processor = PDFProcessor()
        try:
            file_path = pdf_processor.save_file(file_content, organization_id, year, file.filename)
            checksum = pdf_processor.calculate_checksum(file_path)
        finally:
            pdf_processor.cleanup()
        
        # Create report record
        report = Report(
            organization_id=organization_id,
            title=title,
            year=year,
            file_path=file_path,
            status="pending",
            checksum=checksum
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Create ingestion job
        ingestion_service = get_ingestion_service()
        job_data = {
            "kind": "pdf_upload",
            "params": {
                "file_path": file_path,
                "organization_id": organization_id,
                "report_title": title,
                "year": year
            }
        }
        
        from app.schemas import IngestionJobCreate
        job = await ingestion_service.create_ingestion_job(db, IngestionJobCreate(**job_data))
        
        logger.info(f"Uploaded report file: {file.filename} for organization {organization_id}")
        
        return FileUploadResponse(
            filename=file.filename,
            file_path=file_path,
            size=len(file_content),
            checksum=checksum,
            ingestion_job_id=job.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload report"
        )


@router.post("/fetch")
async def fetch_report_from_url(
    organization_id: int,
    title: str,
    year: int,
    url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch a report from URL"""
    try:
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Create ingestion job
        ingestion_service = get_ingestion_service()
        job_data = {
            "kind": "url_fetch",
            "params": {
                "url": url,
                "organization_id": organization_id,
                "report_title": title,
                "year": year
            }
        }
        
        from app.schemas import IngestionJobCreate
        job = await ingestion_service.create_ingestion_job(db, IngestionJobCreate(**job_data))
        
        logger.info(f"Created URL fetch job for: {url}")
        
        return {
            "message": "URL fetch job created",
            "job_id": job.id,
            "url": url,
            "organization_id": organization_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create URL fetch job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create URL fetch job"
        )


@router.put("/{report_id}", response_model=ReportSchema)
async def update_report(
    report_id: int,
    report_update: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a report"""
    try:
        db_report = db.query(Report).filter(Report.id == report_id).first()
        
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Update fields that are provided
        update_data = report_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_report, field, value)
        
        db.commit()
        db.refresh(db_report)
        
        logger.info(f"Updated report: {db_report.title} (ID: {db_report.id})")
        return db_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update report: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update report"
        )


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a report"""
    try:
        db_report = db.query(Report).filter(Report.id == report_id).first()
        
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check if report has associated data
        from app.models import KPIValue, Embedding
        
        kpi_values_count = db.query(KPIValue).filter(KPIValue.report_id == report_id).count()
        embeddings_count = db.query(Embedding).filter(Embedding.report_id == report_id).count()
        
        if kpi_values_count > 0 or embeddings_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete report with associated data ({kpi_values_count} KPI values, {embeddings_count} embeddings)"
            )
        
        # Delete file if it exists
        if db_report.file_path and os.path.exists(db_report.file_path):
            try:
                os.remove(db_report.file_path)
                logger.info(f"Deleted file: {db_report.file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {db_report.file_path}: {e}")
        
        db.delete(db_report)
        db.commit()
        
        logger.info(f"Deleted report: {db_report.title} (ID: {report_id})")
        return {"message": "Report deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )


@router.get("/{report_id}/chunks")
async def get_report_chunks(
    report_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get text chunks from a report"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        from app.models import Embedding
        
        embeddings = db.query(Embedding).filter(
            Embedding.report_id == report_id
        ).limit(limit).all()
        
        chunks = []
        for embedding in embeddings:
            chunks.append({
                "id": embedding.id,
                "text": embedding.chunk_text,
                "metadata": embedding.metadata,
                "created_at": embedding.created_at
            })
        
        return {
            "report_id": report_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report chunks"
        )
