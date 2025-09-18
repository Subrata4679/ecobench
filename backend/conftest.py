import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
import os
import tempfile
import shutil

from app.main import app
from app.database import get_db, Base
from app.config import get_settings
from app.models import *


# Test database setup
@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for testing."""
    with PostgresContainer("postgres:15", driver="psycopg2") as postgres:
        # Install pgvector extension
        postgres.exec("psql -U test -d test -c 'CREATE EXTENSION IF NOT EXISTS vector;'")
        yield postgres


@pytest.fixture(scope="session")
def test_db_url(postgres_container):
    """Get the test database URL."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create test database engine."""
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(test_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_upload_dir():
    """Create a temporary upload directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def mock_settings(temp_upload_dir):
    """Override settings for testing."""
    original_settings = get_settings()
    
    # Create mock settings
    class MockSettings:
        database_url = "sqlite:///./test.db"
        secret_key = "test-secret-key"
        debug = True
        log_level = "DEBUG"
        llm_provider = "mock"
        openai_api_key = ""
        tinyllama_model_path = ""
        max_file_size = 10000000
        upload_dir = temp_upload_dir
    
    mock_settings_instance = MockSettings()
    
    # Override the get_settings function
    import app.config
    app.config.get_settings = lambda: mock_settings_instance
    
    yield mock_settings_instance
    
    # Restore original settings
    app.config.get_settings = lambda: original_settings


# Sample data fixtures
@pytest.fixture
def sample_organization(test_session):
    """Create a sample organization."""
    from app.models import Organization
    org = Organization(
        name="Test Organization",
        industry="Technology",
        size="medium",
        description="A test organization for testing purposes",
        website="https://test.example.com"
    )
    test_session.add(org)
    test_session.commit()
    test_session.refresh(org)
    return org


@pytest.fixture
def sample_user(test_session):
    """Create a sample user."""
    from app.models import User
    user = User(
        email="test@example.com",
        name="Test User",
        is_active=True
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def sample_report(test_session, sample_organization):
    """Create a sample report."""
    from app.models import Report
    report = Report(
        title="Test Sustainability Report",
        organization_id=sample_organization.id,
        year=2023,
        report_type="sustainability",
        status="processed",
        file_path="/test/path/report.pdf",
        file_size=1024000,
        checksum="test-checksum"
    )
    test_session.add(report)
    test_session.commit()
    test_session.refresh(report)
    return report


@pytest.fixture
def sample_kpi_definition(test_session):
    """Create a sample KPI definition."""
    from app.models import KPIDefinition
    kpi = KPIDefinition(
        name="Carbon Emissions",
        description="Total carbon emissions in tons CO2 equivalent",
        category="Environmental",
        unit="tons CO2e",
        calculation_method="Sum of all direct and indirect emissions"
    )
    test_session.add(kpi)
    test_session.commit()
    test_session.refresh(kpi)
    return kpi


@pytest.fixture
def sample_kpi_value(test_session, sample_organization, sample_kpi_definition, sample_report):
    """Create a sample KPI value."""
    from app.models import KPIValue
    value = KPIValue(
        kpi_id=sample_kpi_definition.id,
        organization_id=sample_organization.id,
        report_id=sample_report.id,
        value=1250.5,
        year=2023,
        period="annual",
        source="sustainability_report"
    )
    test_session.add(value)
    test_session.commit()
    test_session.refresh(value)
    return value


@pytest.fixture
def sample_embedding(test_session, sample_report):
    """Create a sample embedding."""
    from app.models import Embedding
    import numpy as np
    
    # Create a sample embedding vector
    embedding_vector = np.random.rand(1536).tolist()
    
    embedding = Embedding(
        report_id=sample_report.id,
        content="This is a sample text chunk for testing embeddings and semantic search functionality.",
        embedding=embedding_vector,
        chunk_index=0,
        page_number=1
    )
    test_session.add(embedding)
    test_session.commit()
    test_session.refresh(embedding)
    return embedding


@pytest.fixture
def sample_ingestion_job(test_session, sample_report):
    """Create a sample ingestion job."""
    from app.models import IngestionJob
    job = IngestionJob(
        report_id=sample_report.id,
        job_type="ingestion",
        status="completed",
        progress=100
    )
    test_session.add(job)
    test_session.commit()
    test_session.refresh(job)
    return job


@pytest.fixture
def sample_peer_group(test_session, sample_organization):
    """Create a sample peer group."""
    from app.models import PeerGroup
    group = PeerGroup(
        name="Tech Companies",
        description="Technology companies for benchmarking"
    )
    test_session.add(group)
    test_session.commit()
    test_session.refresh(group)
    
    # Add organization to peer group
    group.organizations.append(sample_organization)
    test_session.commit()
    
    return group


@pytest.fixture
def sample_recommendation(test_session, sample_organization, sample_kpi_definition):
    """Create a sample recommendation."""
    from app.models import Recommendation
    rec = Recommendation(
        organization_id=sample_organization.id,
        kpi_id=sample_kpi_definition.id,
        title="Reduce Carbon Emissions",
        description="Implement energy efficiency measures to reduce carbon footprint",
        type="improvement",
        priority="high",
        status="pending",
        confidence_score=0.85,
        action_items=["Install LED lighting", "Upgrade HVAC system", "Use renewable energy"]
    )
    test_session.add(rec)
    test_session.commit()
    test_session.refresh(rec)
    return rec


# Authentication fixtures
@pytest.fixture
def auth_headers(client):
    """Get authentication headers for API requests."""
    # Mock login to get token
    response = client.post("/api/auth/mock-login", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Async fixtures for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock LLM client fixture
@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    from app.services.llm_client import MockLLMClient
    return MockLLMClient()


# File upload fixtures
@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Test PDF Document")
    p.drawString(100, 700, "This is a sample PDF for testing purposes.")
    p.drawString(100, 650, "Carbon emissions: 1250.5 tons CO2e")
    p.drawString(100, 600, "Energy consumption: 2500 MWh")
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_file_upload(sample_pdf_file):
    """Create a sample file upload for testing."""
    return {
        "file": ("test_report.pdf", sample_pdf_file, "application/pdf")
    }
