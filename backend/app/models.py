from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


class Organization(Base):
    __tablename__ = "organization"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ticker = Column(String(20), nullable=True)
    sector = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reports = relationship("Report", back_populates="organization")
    kpi_values = relationship("KPIValue", back_populates="organization")
    recommendations = relationship("Recommendation", back_populates="organization")
    regulatory_reports = relationship("RegulatoryReport", back_populates="organization")


class DataSource(Base):
    __tablename__ = "data_source"
    
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # pdf, url, manual
    url = Column(String(1000), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    reports = relationship("Report", back_populates="source")


class Report(Base):
    __tablename__ = "report"
    
    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organization.id"), nullable=False)
    source_id = Column(BigInteger, ForeignKey("data_source.id"), nullable=True)
    title = Column(String(500), nullable=False)
    year = Column(Integer, nullable=False)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    file_path = Column(String(1000), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="reports")
    source = relationship("DataSource", back_populates="reports")
    kpi_values = relationship("KPIValue", back_populates="report")
    embeddings = relationship("Embedding", back_populates="report")


class KPIDefinition(Base):
    __tablename__ = "kpi_definition"
    
    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    framework_tags = Column(JSONB, nullable=True)
    is_higher_better = Column(Boolean, default=False)
    
    # Relationships
    kpi_values = relationship("KPIValue", back_populates="kpi_definition")
    embeddings = relationship("Embedding", back_populates="kpi_definition")
    recommendations = relationship("Recommendation", back_populates="kpi_definition")


class KPIValue(Base):
    __tablename__ = "kpi_value"
    
    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organization.id"), nullable=False)
    kpi_id = Column(BigInteger, ForeignKey("kpi_definition.id"), nullable=False)
    report_id = Column(BigInteger, ForeignKey("report.id"), nullable=True)
    year = Column(Integer, nullable=False)
    value_numeric = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    normalized_to_base_unit = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    extraction_method = Column(String(50), nullable=True)  # manual, regex, llm
    evidence_span = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="kpi_values")
    kpi_definition = relationship("KPIDefinition", back_populates="kpi_values")
    report = relationship("Report", back_populates="kpi_values")
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_kpi_values', 'organization_id', 'kpi_id', 'year'),
    )


class PeerGroup(Base):
    __tablename__ = "peer_group"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    criteria = Column(JSONB, nullable=True)  # sector, size, geography filters
    
    # Relationships
    benchmark_snapshots = relationship("BenchmarkSnapshot", back_populates="peer_group")


class BenchmarkSnapshot(Base):
    __tablename__ = "benchmark_snapshot"
    
    id = Column(BigInteger, primary_key=True, index=True)
    peer_group_id = Column(BigInteger, ForeignKey("peer_group.id"), nullable=False)
    kpi_id = Column(BigInteger, ForeignKey("kpi_definition.id"), nullable=False)
    period = Column(String(20), nullable=False)  # 2023, 2022-2023, etc.
    stats = Column(JSONB, nullable=True)  # min, p25, median, p75, max, count
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    peer_group = relationship("PeerGroup", back_populates="benchmark_snapshots")


class Recommendation(Base):
    __tablename__ = "recommendation"
    
    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organization.id"), nullable=False)
    kpi_id = Column(BigInteger, ForeignKey("kpi_definition.id"), nullable=True)
    title = Column(String(500), nullable=False)
    rationale = Column(Text, nullable=True)
    actions = Column(JSONB, nullable=True)  # structured action items
    confidence = Column(Float, nullable=True)
    sources = Column(JSONB, nullable=True)  # citations and references
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="recommendations")
    kpi_definition = relationship("KPIDefinition", back_populates="recommendations")


class IngestionJob(Base):
    __tablename__ = "ingestion_job"
    
    id = Column(BigInteger, primary_key=True, index=True)
    kind = Column(String(50), nullable=False)  # pdf_upload, url_fetch, extraction
    params = Column(JSONB, nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    logs = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "user"
    
    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    roles = Column(JSONB, default=["user"])
    provider = Column(String(50), default="mock")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="actor_user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    esg_data = relationship("UserESGData", back_populates="user")


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(BigInteger, primary_key=True, index=True)
    actor_user_id = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    actor_user = relationship("User", back_populates="audit_logs")


class Embedding(Base):
    __tablename__ = "embedding"
    
    id = Column(BigInteger, primary_key=True, index=True)
    report_id = Column(BigInteger, ForeignKey("report.id"), nullable=True)
    kpi_definition_id = Column(BigInteger, ForeignKey("kpi_definition.id"), nullable=True)
    chunk_text = Column(Text, nullable=False)
    vector = Column(Vector(1536), nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="embeddings")
    kpi_definition = relationship("KPIDefinition", back_populates="embeddings")
    
    # Vector index for similarity search
    __table_args__ = (
        Index('idx_embedding_vector', 'vector', postgresql_using='ivfflat', 
              postgresql_with={'lists': 64}, postgresql_ops={'vector': 'vector_cosine_ops'}),
    )


class RegulatoryReport(Base):
    __tablename__ = "regulatory_report"
    
    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organization.id"), nullable=False)
    report_type = Column(String(100), nullable=False)  # 10-K, 20-F, CSR, Sustainability Report
    filing_date = Column(DateTime, nullable=True)
    period_end_date = Column(DateTime, nullable=True)
    url = Column(String(1000), nullable=False)
    file_path = Column(String(1000), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    raw_content = Column(Text, nullable=True)
    extracted_data = Column(JSONB, nullable=True)
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="regulatory_reports")
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_regulatory_reports', 'organization_id', 'report_type', 'filing_date'),
    )


class ITCompany(Base):
    __tablename__ = "it_company"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ticker = Column(String(20), nullable=True)
    exchange = Column(String(50), nullable=True)  # NASDAQ, NYSE, etc.
    sector = Column(String(100), default="Information Technology")
    website = Column(String(500), nullable=True)
    sec_cik = Column(String(20), nullable=True)  # SEC Central Index Key
    market_cap = Column(BigInteger, nullable=True)
    employees = Column(Integer, nullable=True)
    headquarters = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    scraping_enabled = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scraping_jobs = relationship("ScrapingJob", back_populates="company")


class ScrapingJob(Base):
    __tablename__ = "scraping_job"
    
    id = Column(BigInteger, primary_key=True, index=True)
    company_id = Column(BigInteger, ForeignKey("it_company.id"), nullable=False)
    job_type = Column(String(50), nullable=False)  # sec_filings, sustainability_reports, investor_relations
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    results_summary = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("ITCompany", back_populates="scraping_jobs")


class ChatSession(Base):
    __tablename__ = "chat_session"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    session_name = Column(String(255), nullable=True)
    context_data = Column(JSONB, nullable=True)  # User's ESG data for comparison
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_message"
    
    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("chat_session.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)  # analysis results, sources, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class UserESGData(Base):
    __tablename__ = "user_esg_data"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    scope1_emissions = Column(Float, nullable=True)  # tCO2e
    scope2_emissions = Column(Float, nullable=True)  # tCO2e
    scope3_emissions = Column(Float, nullable=True)  # tCO2e
    water_consumption = Column(Float, nullable=True)  # m³
    waste_generated = Column(Float, nullable=True)  # tonnes
    energy_consumption = Column(Float, nullable=True)  # MWh
    renewable_energy_percentage = Column(Float, nullable=True)  # %
    employee_count = Column(Integer, nullable=True)
    revenue = Column(Float, nullable=True)  # USD
    additional_metrics = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="esg_data")
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_user_esg_data', 'user_id', 'year'),
    )
