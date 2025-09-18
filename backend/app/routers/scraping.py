"""
API endpoints for web scraping functionality
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging

from app.database import get_db
from app.models import ITCompany, ScrapingJob, RegulatoryReport, User
from app.services.scraping_service import scraping_service
from app.routers.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ITCompanyResponse(BaseModel):
    id: int
    name: str
    ticker: Optional[str]
    exchange: Optional[str]
    website: Optional[str]
    sec_cik: Optional[str]
    is_active: bool
    scraping_enabled: bool
    last_scraped: Optional[str]
    
    class Config:
        from_attributes = True


class ScrapingJobResponse(BaseModel):
    id: int
    company_id: int
    job_type: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    results_summary: Optional[Dict]
    
    class Config:
        from_attributes = True


class RegulatoryReportResponse(BaseModel):
    id: int
    organization_id: int
    report_type: str
    filing_date: Optional[str]
    url: str
    status: str
    last_scraped: Optional[str]
    
    class Config:
        from_attributes = True


class ScrapingJobRequest(BaseModel):
    company_id: int
    job_type: str  # 'sec_filings', 'sustainability_reports', 'investor_relations', 'all'


@router.get("/companies", response_model=List[ITCompanyResponse])
async def get_it_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of IT companies available for scraping"""
    
    companies = db.query(ITCompany).offset(skip).limit(limit).all()
    
    return [
        ITCompanyResponse(
            id=company.id,
            name=company.name,
            ticker=company.ticker,
            exchange=company.exchange,
            website=company.website,
            sec_cik=company.sec_cik,
            is_active=company.is_active,
            scraping_enabled=company.scraping_enabled,
            last_scraped=company.last_scraped.isoformat() if company.last_scraped else None
        )
        for company in companies
    ]


@router.post("/initialize-companies")
async def initialize_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize IT companies in the database"""
    
    try:
        companies = await scraping_service.initialize_companies(db)
        
        return {
            "message": f"Successfully initialized {len(companies)} IT companies",
            "companies": [
                {
                    "id": company.id,
                    "name": company.name,
                    "ticker": company.ticker
                }
                for company in companies
            ]
        }
    
    except Exception as e:
        logger.error(f"Error initializing companies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize companies: {str(e)}")


@router.post("/jobs", response_model=Dict)
async def create_scraping_job(
    job_request: ScrapingJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new scraping job for a specific company"""
    
    # Validate company exists
    company = db.query(ITCompany).filter(ITCompany.id == job_request.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.scraping_enabled:
        raise HTTPException(status_code=400, detail="Scraping is disabled for this company")
    
    # Validate job type
    valid_job_types = ['sec_filings', 'sustainability_reports', 'investor_relations', 'all']
    if job_request.job_type not in valid_job_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid job type. Must be one of: {', '.join(valid_job_types)}"
        )
    
    try:
        # Run scraping job in background
        background_tasks.add_task(
            scraping_service.run_scraping_job,
            job_request.company_id,
            job_request.job_type,
            db
        )
        
        return {
            "message": f"Scraping job started for {company.name}",
            "company": company.name,
            "job_type": job_request.job_type,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Error creating scraping job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create scraping job: {str(e)}")


@router.post("/bulk-scraping")
async def run_bulk_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run scraping for all active IT companies"""
    
    try:
        # Run bulk scraping in background
        background_tasks.add_task(scraping_service.run_bulk_scraping, db)
        
        return {
            "message": "Bulk scraping job started for all active IT companies",
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Error starting bulk scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start bulk scraping: {str(e)}")


@router.get("/jobs", response_model=List[ScrapingJobResponse])
async def get_scraping_jobs(
    company_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraping jobs with optional filtering"""
    
    query = db.query(ScrapingJob)
    
    if company_id:
        query = query.filter(ScrapingJob.company_id == company_id)
    
    if status:
        query = query.filter(ScrapingJob.status == status)
    
    jobs = query.order_by(ScrapingJob.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        ScrapingJobResponse(
            id=job.id,
            company_id=job.company_id,
            job_type=job.job_type,
            status=job.status,
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            error_message=job.error_message,
            results_summary=job.results_summary
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=ScrapingJobResponse)
async def get_scraping_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific scraping job"""
    
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    
    return ScrapingJobResponse(
        id=job.id,
        company_id=job.company_id,
        job_type=job.job_type,
        status=job.status,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error_message=job.error_message,
        results_summary=job.results_summary
    )


@router.get("/regulatory-reports", response_model=List[RegulatoryReportResponse])
async def get_regulatory_reports(
    company_name: Optional[str] = None,
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get regulatory reports with optional filtering"""
    
    from app.models import Organization
    
    query = db.query(RegulatoryReport).join(Organization)
    
    if company_name:
        query = query.filter(Organization.name.ilike(f"%{company_name}%"))
    
    if report_type:
        query = query.filter(RegulatoryReport.report_type == report_type)
    
    reports = query.order_by(RegulatoryReport.filing_date.desc()).offset(skip).limit(limit).all()
    
    return [
        RegulatoryReportResponse(
            id=report.id,
            organization_id=report.organization_id,
            report_type=report.report_type,
            filing_date=report.filing_date.isoformat() if report.filing_date else None,
            url=report.url,
            status=report.status,
            last_scraped=report.last_scraped.isoformat() if report.last_scraped else None
        )
        for report in reports
    ]


@router.get("/regulatory-reports/{report_id}", response_model=RegulatoryReportResponse)
async def get_regulatory_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific regulatory report"""
    
    report = db.query(RegulatoryReport).filter(RegulatoryReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Regulatory report not found")
    
    return RegulatoryReportResponse(
        id=report.id,
        organization_id=report.organization_id,
        report_type=report.report_type,
        filing_date=report.filing_date.isoformat() if report.filing_date else None,
        url=report.url,
        status=report.status,
        last_scraped=report.last_scraped.isoformat() if report.last_scraped else None
    )


@router.put("/companies/{company_id}/toggle-scraping")
async def toggle_company_scraping(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable or disable scraping for a specific company"""
    
    company = db.query(ITCompany).filter(ITCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.scraping_enabled = not company.scraping_enabled
    db.commit()
    
    return {
        "message": f"Scraping {'enabled' if company.scraping_enabled else 'disabled'} for {company.name}",
        "company": company.name,
        "scraping_enabled": company.scraping_enabled
    }


@router.get("/stats")
async def get_scraping_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraping statistics"""
    
    from sqlalchemy import func
    
    # Count companies
    total_companies = db.query(func.count(ITCompany.id)).scalar()
    active_companies = db.query(func.count(ITCompany.id)).filter(
        ITCompany.scraping_enabled == True
    ).scalar()
    
    # Count jobs by status
    job_stats = db.query(
        ScrapingJob.status,
        func.count(ScrapingJob.id)
    ).group_by(ScrapingJob.status).all()
    
    # Count reports by type
    report_stats = db.query(
        RegulatoryReport.report_type,
        func.count(RegulatoryReport.id)
    ).group_by(RegulatoryReport.report_type).all()
    
    return {
        "companies": {
            "total": total_companies,
            "active": active_companies,
            "inactive": total_companies - active_companies
        },
        "jobs": {status: count for status, count in job_stats},
        "reports": {report_type: count for report_type, count in report_stats}
    }
