import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.ingestion import IngestionService
from app.models import Report, IngestionJob, Embedding


@pytest.mark.unit
class TestIngestionService:
    """Test IngestionService functionality."""
    
    @pytest.fixture
    def ingestion_service(self, test_session, mock_llm_client):
        """Create ingestion service instance."""
        return IngestionService(test_session, mock_llm_client)
    
    @patch('app.services.ingestion.extract_text_from_pdf')
    def test_process_pdf_report(self, mock_extract, ingestion_service, sample_report, temp_upload_dir):
        """Test processing a PDF report."""
        # Mock PDF text extraction
        mock_extract.return_value = "This is extracted text from PDF. Carbon emissions: 1250.5 tons CO2e."
        
        # Create a temporary PDF file
        pdf_path = os.path.join(temp_upload_dir, "test.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"fake pdf content")
        
        sample_report.file_path = pdf_path
        
        # Process the report
        result = ingestion_service.process_report(sample_report.id)
        
        assert result is True
        mock_extract.assert_called_once_with(pdf_path)
    
    def test_create_ingestion_job(self, ingestion_service, sample_report):
        """Test creating an ingestion job."""
        job = ingestion_service.create_ingestion_job(
            report_id=sample_report.id,
            job_type="ingestion"
        )
        
        assert job.report_id == sample_report.id
        assert job.job_type == "ingestion"
        assert job.status == "pending"
        assert job.progress == 0
    
    def test_update_job_progress(self, ingestion_service, sample_ingestion_job):
        """Test updating job progress."""
        ingestion_service.update_job_progress(
            job_id=sample_ingestion_job.id,
            progress=50,
            status="running"
        )
        
        assert sample_ingestion_job.progress == 50
        assert sample_ingestion_job.status == "running"
    
    @patch('app.services.ingestion.chunk_text')
    def test_create_embeddings(self, mock_chunk, ingestion_service, sample_report):
        """Test creating embeddings from text."""
        # Mock text chunking
        mock_chunk.return_value = [
            "First chunk of text about sustainability.",
            "Second chunk about carbon emissions."
        ]
        
        text = "Full text content for embedding generation."
        
        embeddings = ingestion_service.create_embeddings(sample_report.id, text)
        
        assert len(embeddings) == 2
        for embedding in embeddings:
            assert embedding.report_id == sample_report.id
            assert len(embedding.embedding) == 1536  # Mock embedding size
            assert embedding.content is not None
    
    @patch('requests.get')
    def test_fetch_report_from_url(self, mock_get, ingestion_service, sample_organization, temp_upload_dir):
        """Test fetching report from URL."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.content = b"fake pdf content"
        mock_response.headers = {"content-type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        report_data = {
            "title": "Remote Report",
            "organization_id": sample_organization.id,
            "year": 2023,
            "report_type": "sustainability",
            "url": "https://example.com/report.pdf"
        }
        
        with patch('app.services.ingestion.get_settings') as mock_settings:
            mock_settings.return_value.upload_dir = temp_upload_dir
            
            report = ingestion_service.fetch_report_from_url(report_data)
        
        assert report.title == "Remote Report"
        assert report.status == "uploaded"
        assert report.file_path is not None
        mock_get.assert_called_once_with("https://example.com/report.pdf", timeout=30)
    
    def test_run_extraction_job(self, ingestion_service, sample_report, sample_ingestion_job):
        """Test running an extraction job."""
        # Set up job for extraction
        sample_ingestion_job.job_type = "extraction"
        sample_ingestion_job.status = "pending"
        
        with patch.object(ingestion_service, '_extract_kpis_from_report') as mock_extract:
            mock_extract.return_value = [
                {"name": "Carbon Emissions", "value": 1250.5, "unit": "tons CO2e", "confidence": 0.9}
            ]
            
            result = ingestion_service.run_extraction_job(sample_ingestion_job.id)
        
        assert result is True
        assert sample_ingestion_job.status == "completed"
        mock_extract.assert_called_once()


@pytest.mark.integration
class TestIngestionServiceIntegration:
    """Integration tests for IngestionService."""
    
    @pytest.fixture
    def ingestion_service(self, test_session):
        """Create ingestion service with real LLM client."""
        from app.services.llm_client import MockLLMClient
        return IngestionService(test_session, MockLLMClient())
    
    def test_full_ingestion_workflow(self, ingestion_service, sample_organization, temp_upload_dir):
        """Test complete ingestion workflow."""
        # Create a report
        report_data = {
            "title": "Test Report",
            "organization_id": sample_organization.id,
            "year": 2023,
            "report_type": "sustainability"
        }
        
        # Create temporary file
        file_path = os.path.join(temp_upload_dir, "test.pdf")
        with open(file_path, "wb") as f:
            f.write(b"fake pdf content")
        
        with patch('app.services.ingestion.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Carbon emissions decreased by 15% to 1250.5 tons CO2e."
            
            # Create and process report
            from app.models import Report
            report = Report(**report_data, file_path=file_path, status="uploaded")
            ingestion_service.db.add(report)
            ingestion_service.db.commit()
            
            # Create ingestion job
            job = ingestion_service.create_ingestion_job(report.id, "ingestion")
            
            # Process the report
            result = ingestion_service.process_report(report.id)
            
            assert result is True
            assert job.status == "completed"
            
            # Check embeddings were created
            embeddings = ingestion_service.db.query(Embedding).filter_by(report_id=report.id).all()
            assert len(embeddings) > 0
