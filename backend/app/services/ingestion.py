import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import httpx
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, IngestionJob, Embedding, Organization
from app.schemas import IngestionJobCreate
from app.utils.pdf_utils import PDFProcessor, extract_pdf_text, chunk_document_text
from app.services.llm_client import get_llm_client_instance
from app.config import settings

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for handling document ingestion and processing"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.llm_client = get_llm_client_instance()
    
    async def create_ingestion_job(self, db: Session, job_data: IngestionJobCreate) -> IngestionJob:
        """Create a new ingestion job"""
        job = IngestionJob(
            kind=job_data.kind,
            params=job_data.params,
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Created ingestion job {job.id} of type {job.kind}")
        return job
    
    async def update_job_status(self, db: Session, job_id: int, status: str, logs: str = None):
        """Update job status and logs"""
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.status = status
            if logs:
                job.logs = (job.logs or "") + f"\n{datetime.now().isoformat()}: {logs}"
            
            if status == "running":
                job.started_at = datetime.now()
            elif status in ["completed", "failed"]:
                job.finished_at = datetime.now()
            
            db.commit()
            logger.info(f"Updated job {job_id} status to {status}")
    
    async def process_pdf_upload(self, db: Session, job_id: int, file_path: str, 
                                organization_id: int, report_title: str, year: int) -> Dict[str, Any]:
        """Process uploaded PDF file"""
        try:
            await self.update_job_status(db, job_id, "running", "Starting PDF processing")
            
            # Extract text from PDF
            extraction_result = extract_pdf_text(file_path)
            
            if not extraction_result["success"]:
                await self.update_job_status(db, job_id, "failed", 
                                           f"PDF extraction failed: {extraction_result['errors']}")
                return {"success": False, "error": "PDF extraction failed"}
            
            await self.update_job_status(db, job_id, "running", 
                                       f"Extracted text using {extraction_result['extraction_method']}")
            
            # Create or update report record
            report = db.query(Report).filter(
                Report.organization_id == organization_id,
                Report.file_path == file_path
            ).first()
            
            if not report:
                report = Report(
                    organization_id=organization_id,
                    title=report_title,
                    year=year,
                    file_path=file_path,
                    status="processing",
                    checksum=extraction_result["checksum"]
                )
                db.add(report)
                db.commit()
                db.refresh(report)
            
            # Chunk the text
            chunks = chunk_document_text(extraction_result["text_content"])
            await self.update_job_status(db, job_id, "running", 
                                       f"Created {len(chunks)} text chunks")
            
            # Generate embeddings for chunks
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.llm_client.generate_embeddings(chunk_texts)
            
            await self.update_job_status(db, job_id, "running", 
                                       f"Generated embeddings for {len(embeddings)} chunks")
            
            # Store embeddings in database
            embedding_records = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                embedding_record = Embedding(
                    report_id=report.id,
                    chunk_text=chunk["text"],
                    vector=embedding,
                    metadata={
                        "chunk_id": chunk["chunk_id"],
                        "start_pos": chunk["start_pos"],
                        "end_pos": chunk["end_pos"],
                        "length": chunk["length"],
                        "extraction_method": extraction_result["extraction_method"],
                        "page_info": extraction_result["page_info"]
                    }
                )
                embedding_records.append(embedding_record)
            
            db.add_all(embedding_records)
            db.commit()
            
            # Update report status
            report.status = "completed"
            db.commit()
            
            await self.update_job_status(db, job_id, "completed", 
                                       f"Successfully processed PDF with {len(embedding_records)} embeddings")
            
            return {
                "success": True,
                "report_id": report.id,
                "chunks_processed": len(chunks),
                "embeddings_created": len(embedding_records),
                "extraction_method": extraction_result["extraction_method"]
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed for job {job_id}: {e}")
            await self.update_job_status(db, job_id, "failed", f"Processing error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_url_fetch(self, db: Session, job_id: int, url: str, 
                               organization_id: int, report_title: str, year: int) -> Dict[str, Any]:
        """Fetch and process document from URL"""
        try:
            await self.update_job_status(db, job_id, "running", f"Fetching document from {url}")
            
            # Download file from URL
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Determine file type from content-type or URL
                content_type = response.headers.get("content-type", "")
                if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                    await self.update_job_status(db, job_id, "failed", 
                                               f"Unsupported file type: {content_type}")
                    return {"success": False, "error": f"Unsupported file type: {content_type}"}
                
                # Save file temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
            
            # Save to permanent location
            filename = url.split("/")[-1] or f"report_{year}.pdf"
            file_path = self.pdf_processor.save_file(
                response.content, organization_id, year, filename
            )
            
            # Process the downloaded PDF
            result = await self.process_pdf_upload(
                db, job_id, file_path, organization_id, report_title, year
            )
            
            # Clean up temp file
            import os
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"URL fetch failed for job {job_id}: {e}")
            await self.update_job_status(db, job_id, "failed", f"URL fetch error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_extraction_job(self, db: Session, job_id: int, report_id: int) -> Dict[str, Any]:
        """Process KPI extraction for a report"""
        try:
            await self.update_job_status(db, job_id, "running", "Starting KPI extraction")
            
            # Get report and organization info
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                await self.update_job_status(db, job_id, "failed", "Report not found")
                return {"success": False, "error": "Report not found"}
            
            organization = db.query(Organization).filter(Organization.id == report.organization_id).first()
            
            # Get embeddings for the report
            embeddings = db.query(Embedding).filter(Embedding.report_id == report_id).all()
            
            if not embeddings:
                await self.update_job_status(db, job_id, "failed", "No embeddings found for report")
                return {"success": False, "error": "No embeddings found"}
            
            extracted_kpis = []
            
            # Process each chunk for KPI extraction
            for embedding in embeddings:
                context = {
                    "org": organization.name if organization else "Unknown",
                    "year": report.year,
                    "report_title": report.title
                }
                
                # Extract KPIs from chunk
                chunk_kpis = await self.llm_client.extract_kpis_from_chunk(
                    embedding.chunk_text, context
                )
                
                # Add chunk metadata to extracted KPIs
                for kpi in chunk_kpis:
                    kpi["chunk_id"] = embedding.id
                    kpi["report_id"] = report_id
                    extracted_kpis.append(kpi)
            
            await self.update_job_status(db, job_id, "completed", 
                                       f"Extracted {len(extracted_kpis)} KPI values")
            
            return {
                "success": True,
                "report_id": report_id,
                "extracted_kpis": extracted_kpis,
                "chunks_processed": len(embeddings)
            }
            
        except Exception as e:
            logger.error(f"KPI extraction failed for job {job_id}: {e}")
            await self.update_job_status(db, job_id, "failed", f"Extraction error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_job(self, db: Session, job_id: int) -> Dict[str, Any]:
        """Run an ingestion job based on its type"""
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return {"success": False, "error": "Job not found"}
        
        if job.status != "pending":
            return {"success": False, "error": f"Job is not pending (status: {job.status})"}
        
        params = job.params or {}
        
        try:
            if job.kind == "pdf_upload":
                return await self.process_pdf_upload(
                    db, job_id,
                    params["file_path"],
                    params["organization_id"],
                    params["report_title"],
                    params["year"]
                )
            
            elif job.kind == "url_fetch":
                return await self.process_url_fetch(
                    db, job_id,
                    params["url"],
                    params["organization_id"],
                    params["report_title"],
                    params["year"]
                )
            
            elif job.kind == "extraction":
                return await self.process_extraction_job(
                    db, job_id,
                    params["report_id"]
                )
            
            else:
                await self.update_job_status(db, job_id, "failed", f"Unknown job kind: {job.kind}")
                return {"success": False, "error": f"Unknown job kind: {job.kind}"}
                
        except Exception as e:
            logger.error(f"Job {job_id} execution failed: {e}")
            await self.update_job_status(db, job_id, "failed", f"Execution error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Clean up resources"""
        self.pdf_processor.cleanup()


# Global service instance
_ingestion_service = None

def get_ingestion_service() -> IngestionService:
    """Get singleton ingestion service instance"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
