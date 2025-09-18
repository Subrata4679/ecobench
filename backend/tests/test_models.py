import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import (
    Organization, User, Report, KPIDefinition, KPIValue, 
    Embedding, IngestionJob, PeerGroup, BenchmarkSnapshot, 
    Recommendation, AuditLog
)


@pytest.mark.unit
class TestOrganization:
    """Test Organization model."""
    
    def test_create_organization(self, test_session):
        """Test creating an organization."""
        org = Organization(
            name="Test Corp",
            industry="Technology",
            size="medium"
        )
        test_session.add(org)
        test_session.commit()
        
        assert org.id is not None
        assert org.name == "Test Corp"
        assert org.industry == "Technology"
        assert org.size == "medium"
        assert org.created_at is not None
        assert org.updated_at is not None
    
    def test_organization_name_required(self, test_session):
        """Test that organization name is required."""
        org = Organization(industry="Technology")
        test_session.add(org)
        
        with pytest.raises(IntegrityError):
            test_session.commit()
    
    def test_organization_relationships(self, test_session, sample_organization):
        """Test organization relationships."""
        # Test reports relationship
        report = Report(
            title="Test Report",
            organization_id=sample_organization.id,
            year=2023,
            report_type="sustainability"
        )
        test_session.add(report)
        test_session.commit()
        
        test_session.refresh(sample_organization)
        assert len(sample_organization.reports) == 1
        assert sample_organization.reports[0].title == "Test Report"


@pytest.mark.unit
class TestUser:
    """Test User model."""
    
    def test_create_user(self, test_session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            name="Test User"
        )
        test_session.add(user)
        test_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_email_unique(self, test_session):
        """Test that user email is unique."""
        user1 = User(email="test@example.com", name="User 1")
        user2 = User(email="test@example.com", name="User 2")
        
        test_session.add(user1)
        test_session.commit()
        
        test_session.add(user2)
        with pytest.raises(IntegrityError):
            test_session.commit()


@pytest.mark.unit
class TestReport:
    """Test Report model."""
    
    def test_create_report(self, test_session, sample_organization):
        """Test creating a report."""
        report = Report(
            title="Sustainability Report 2023",
            organization_id=sample_organization.id,
            year=2023,
            report_type="sustainability",
            status="uploaded"
        )
        test_session.add(report)
        test_session.commit()
        
        assert report.id is not None
        assert report.title == "Sustainability Report 2023"
        assert report.year == 2023
        assert report.status == "uploaded"
        assert report.created_at is not None
    
    def test_report_organization_relationship(self, test_session, sample_report):
        """Test report-organization relationship."""
        assert sample_report.organization is not None
        assert sample_report.organization.name == "Test Organization"


@pytest.mark.unit
class TestKPIDefinition:
    """Test KPIDefinition model."""
    
    def test_create_kpi_definition(self, test_session):
        """Test creating a KPI definition."""
        kpi = KPIDefinition(
            name="Water Consumption",
            description="Total water consumption in cubic meters",
            category="Environmental",
            unit="m³"
        )
        test_session.add(kpi)
        test_session.commit()
        
        assert kpi.id is not None
        assert kpi.name == "Water Consumption"
        assert kpi.category == "Environmental"
        assert kpi.unit == "m³"
    
    def test_kpi_name_unique(self, test_session):
        """Test that KPI name is unique."""
        kpi1 = KPIDefinition(name="Carbon Emissions", category="Environmental")
        kpi2 = KPIDefinition(name="Carbon Emissions", category="Environmental")
        
        test_session.add(kpi1)
        test_session.commit()
        
        test_session.add(kpi2)
        with pytest.raises(IntegrityError):
            test_session.commit()


@pytest.mark.unit
class TestKPIValue:
    """Test KPIValue model."""
    
    def test_create_kpi_value(self, test_session, sample_organization, sample_kpi_definition, sample_report):
        """Test creating a KPI value."""
        value = KPIValue(
            kpi_id=sample_kpi_definition.id,
            organization_id=sample_organization.id,
            report_id=sample_report.id,
            value=1500.0,
            year=2023,
            period="annual"
        )
        test_session.add(value)
        test_session.commit()
        
        assert value.id is not None
        assert value.value == 1500.0
        assert value.year == 2023
        assert value.period == "annual"
    
    def test_kpi_value_relationships(self, test_session, sample_kpi_value):
        """Test KPI value relationships."""
        assert sample_kpi_value.kpi is not None
        assert sample_kpi_value.organization is not None
        assert sample_kpi_value.report is not None
        assert sample_kpi_value.kpi.name == "Carbon Emissions"


@pytest.mark.unit
class TestEmbedding:
    """Test Embedding model."""
    
    def test_create_embedding(self, test_session, sample_report):
        """Test creating an embedding."""
        import numpy as np
        
        embedding_vector = np.random.rand(1536).tolist()
        embedding = Embedding(
            report_id=sample_report.id,
            content="Sample text content",
            embedding=embedding_vector,
            chunk_index=0
        )
        test_session.add(embedding)
        test_session.commit()
        
        assert embedding.id is not None
        assert embedding.content == "Sample text content"
        assert len(embedding.embedding) == 1536
        assert embedding.chunk_index == 0


@pytest.mark.unit
class TestIngestionJob:
    """Test IngestionJob model."""
    
    def test_create_ingestion_job(self, test_session, sample_report):
        """Test creating an ingestion job."""
        job = IngestionJob(
            report_id=sample_report.id,
            job_type="ingestion",
            status="pending"
        )
        test_session.add(job)
        test_session.commit()
        
        assert job.id is not None
        assert job.job_type == "ingestion"
        assert job.status == "pending"
        assert job.progress == 0
        assert job.created_at is not None
    
    def test_job_status_update(self, test_session, sample_ingestion_job):
        """Test updating job status."""
        sample_ingestion_job.status = "running"
        sample_ingestion_job.progress = 50
        test_session.commit()
        
        test_session.refresh(sample_ingestion_job)
        assert sample_ingestion_job.status == "running"
        assert sample_ingestion_job.progress == 50


@pytest.mark.unit
class TestPeerGroup:
    """Test PeerGroup model."""
    
    def test_create_peer_group(self, test_session):
        """Test creating a peer group."""
        group = PeerGroup(
            name="Manufacturing Companies",
            description="Companies in manufacturing sector"
        )
        test_session.add(group)
        test_session.commit()
        
        assert group.id is not None
        assert group.name == "Manufacturing Companies"
        assert group.description == "Companies in manufacturing sector"
    
    def test_peer_group_organizations(self, test_session, sample_peer_group, sample_organization):
        """Test peer group organization relationships."""
        assert len(sample_peer_group.organizations) == 1
        assert sample_peer_group.organizations[0].id == sample_organization.id


@pytest.mark.unit
class TestBenchmarkSnapshot:
    """Test BenchmarkSnapshot model."""
    
    def test_create_benchmark_snapshot(self, test_session, sample_kpi_definition):
        """Test creating a benchmark snapshot."""
        snapshot = BenchmarkSnapshot(
            kpi_id=sample_kpi_definition.id,
            year=2023,
            organization_count=10,
            avg_value=1250.5,
            min_value=800.0,
            max_value=2000.0,
            percentile_25=1000.0,
            percentile_50=1200.0,
            percentile_75=1500.0
        )
        test_session.add(snapshot)
        test_session.commit()
        
        assert snapshot.id is not None
        assert snapshot.year == 2023
        assert snapshot.organization_count == 10
        assert snapshot.avg_value == 1250.5


@pytest.mark.unit
class TestRecommendation:
    """Test Recommendation model."""
    
    def test_create_recommendation(self, test_session, sample_organization, sample_kpi_definition):
        """Test creating a recommendation."""
        rec = Recommendation(
            organization_id=sample_organization.id,
            kpi_id=sample_kpi_definition.id,
            title="Improve Energy Efficiency",
            description="Implement energy-saving measures",
            type="improvement",
            priority="medium",
            status="pending",
            confidence_score=0.75
        )
        test_session.add(rec)
        test_session.commit()
        
        assert rec.id is not None
        assert rec.title == "Improve Energy Efficiency"
        assert rec.priority == "medium"
        assert rec.confidence_score == 0.75
    
    def test_recommendation_relationships(self, test_session, sample_recommendation):
        """Test recommendation relationships."""
        assert sample_recommendation.organization is not None
        assert sample_recommendation.kpi is not None
        assert sample_recommendation.organization.name == "Test Organization"


@pytest.mark.unit
class TestAuditLog:
    """Test AuditLog model."""
    
    def test_create_audit_log(self, test_session, sample_user):
        """Test creating an audit log entry."""
        log = AuditLog(
            user_id=sample_user.id,
            action="CREATE",
            resource_type="Organization",
            resource_id=1,
            details={"name": "Test Corp"}
        )
        test_session.add(log)
        test_session.commit()
        
        assert log.id is not None
        assert log.action == "CREATE"
        assert log.resource_type == "Organization"
        assert log.details["name"] == "Test Corp"
        assert log.timestamp is not None
