from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LLMProviderEnum(str, Enum):
    TINYLLAMA = "tinyllama"
    OPENAI = "openai"
    MOCK = "mock"


class JobTypeEnum(str, Enum):
    SEC_FILINGS = "sec_filings"
    SUSTAINABILITY_REPORTS = "sustainability_reports"
    INVESTOR_RELATIONS = "investor_relations"
    ALL = "all"


class ChatRoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Organization schemas
class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)
    ticker: Optional[str] = Field(None, max_length=20)
    sector: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    ticker: Optional[str] = Field(None, max_length=20)
    sector: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)


class Organization(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Report schemas
class ReportBase(BaseModel):
    title: str = Field(..., max_length=500)
    year: int = Field(..., ge=1900, le=2100)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class ReportCreate(ReportBase):
    organization_id: int
    source_id: Optional[int] = None


class ReportUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    status: Optional[StatusEnum] = None


class Report(ReportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    source_id: Optional[int] = None
    file_path: Optional[str] = None
    status: str = "pending"
    checksum: Optional[str] = None
    created_at: datetime


# KPI Definition schemas
class KPIDefinitionBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    unit: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    framework_tags: Optional[Dict[str, Any]] = None
    is_higher_better: bool = False


class KPIDefinitionCreate(KPIDefinitionBase):
    pass


class KPIDefinition(KPIDefinitionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


# KPI Value schemas
class KPIValueBase(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    value_numeric: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    normalized_to_base_unit: Optional[float] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    extraction_method: Optional[str] = Field(None, max_length=50)
    evidence_span: Optional[Dict[str, Any]] = None


class KPIValueCreate(KPIValueBase):
    organization_id: int
    kpi_id: int
    report_id: Optional[int] = None


class KPIValue(KPIValueBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    kpi_id: int
    report_id: Optional[int] = None
    created_at: datetime


# Ingestion Job schemas
class IngestionJobBase(BaseModel):
    kind: str = Field(..., max_length=50)
    params: Optional[Dict[str, Any]] = None


class IngestionJobCreate(IngestionJobBase):
    pass


class IngestionJob(IngestionJobBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str = "pending"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    logs: Optional[str] = None


# User schemas
class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    roles: List[str] = ["user"]
    provider: str = "mock"


class UserCreate(UserBase):
    pass


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class MockLoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)


# Search schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=100)
    organization_id: Optional[int] = None
    kpi_id: Optional[int] = None


class SearchResult(BaseModel):
    chunk_text: str
    similarity_score: float
    report_id: Optional[int] = None
    kpi_definition_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


# Extraction schemas
class ExtractedKPI(BaseModel):
    kpi_code: str
    value: Optional[float] = None
    unit: Optional[str] = None
    year: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_start: int
    evidence_end: int
    page_number: Optional[int] = None


class ExtractionResult(BaseModel):
    extracted_kpis: List[ExtractedKPI]
    chunk_text: str
    processing_time: float


# Benchmark schemas
class BenchmarkStats(BaseModel):
    min_value: Optional[float] = None
    p25: Optional[float] = None
    median: Optional[float] = None
    p75: Optional[float] = None
    max_value: Optional[float] = None
    count: int = 0


class BenchmarkRequest(BaseModel):
    peer_group_id: int
    kpi_id: int
    period: str = Field(..., max_length=20)


class BenchmarkSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    peer_group_id: int
    kpi_id: int
    period: str
    stats: BenchmarkStats
    created_at: datetime


# Recommendation schemas
class RecommendationAction(BaseModel):
    step: str
    impact: str
    effort: str = Field(..., regex="^(low|medium|high)$")
    owner: str
    timeframe: str


class RecommendationSource(BaseModel):
    org: str
    report: str
    page: Optional[int] = None
    url: Optional[str] = None


class RecommendationBase(BaseModel):
    title: str = Field(..., max_length=500)
    rationale: Optional[str] = None
    actions: List[RecommendationAction] = []
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    sources: List[RecommendationSource] = []


class RecommendationCreate(RecommendationBase):
    organization_id: int
    kpi_id: Optional[int] = None


class Recommendation(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    kpi_id: Optional[int] = None
    created_at: datetime


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    size: int
    checksum: str
    ingestion_job_id: int


# IT Company schemas
class ITCompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    ticker: Optional[str] = Field(None, max_length=20)
    exchange: Optional[str] = Field(None, max_length=50)
    sector: str = Field(default="Information Technology", max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    sec_cik: Optional[str] = Field(None, max_length=20)
    market_cap: Optional[int] = None
    employees: Optional[int] = None
    headquarters: Optional[str] = Field(None, max_length=255)
    is_active: bool = True
    scraping_enabled: bool = True


class ITCompanyCreate(ITCompanyBase):
    pass


class ITCompany(ITCompanyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_scraped: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Scraping Job schemas
class ScrapingJobBase(BaseModel):
    company_id: int
    job_type: JobTypeEnum


class ScrapingJobCreate(ScrapingJobBase):
    pass


class ScrapingJob(ScrapingJobBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: StatusEnum
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results_summary: Optional[Dict[str, Any]] = None
    created_at: datetime


# Regulatory Report schemas
class RegulatoryReportBase(BaseModel):
    organization_id: int
    report_type: str = Field(..., max_length=100)
    filing_date: Optional[datetime] = None
    period_end_date: Optional[datetime] = None
    url: str = Field(..., max_length=1000)
    file_path: Optional[str] = Field(None, max_length=1000)
    status: StatusEnum = StatusEnum.PENDING
    raw_content: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class RegulatoryReportCreate(RegulatoryReportBase):
    pass


class RegulatoryReport(RegulatoryReportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_scraped: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# User ESG Data schemas
class UserESGDataBase(BaseModel):
    company_name: str = Field(..., max_length=255)
    year: int = Field(..., ge=2000, le=2030)
    scope1_emissions: Optional[float] = Field(None, ge=0)
    scope2_emissions: Optional[float] = Field(None, ge=0)
    scope3_emissions: Optional[float] = Field(None, ge=0)
    water_consumption: Optional[float] = Field(None, ge=0)
    waste_generated: Optional[float] = Field(None, ge=0)
    energy_consumption: Optional[float] = Field(None, ge=0)
    renewable_energy_percentage: Optional[float] = Field(None, ge=0, le=100)
    employee_count: Optional[int] = Field(None, ge=1)
    revenue: Optional[float] = Field(None, ge=0)
    additional_metrics: Optional[Dict[str, Any]] = None


class UserESGDataCreate(UserESGDataBase):
    pass


class UserESGDataUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=2000, le=2030)
    scope1_emissions: Optional[float] = Field(None, ge=0)
    scope2_emissions: Optional[float] = Field(None, ge=0)
    scope3_emissions: Optional[float] = Field(None, ge=0)
    water_consumption: Optional[float] = Field(None, ge=0)
    waste_generated: Optional[float] = Field(None, ge=0)
    energy_consumption: Optional[float] = Field(None, ge=0)
    renewable_energy_percentage: Optional[float] = Field(None, ge=0, le=100)
    employee_count: Optional[int] = Field(None, ge=1)
    revenue: Optional[float] = Field(None, ge=0)
    additional_metrics: Optional[Dict[str, Any]] = None


class UserESGData(UserESGDataBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Chat Session schemas
class ChatSessionBase(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255)
    context_data: Optional[Dict[str, Any]] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSession(ChatSessionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Chat Message schemas
class ChatMessageBase(BaseModel):
    role: ChatRoleEnum
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessage(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    created_at: datetime


# ESG Analysis schemas
class MetricAnalysis(BaseModel):
    user_value: float
    industry_median: float
    industry_mean: float
    percentile: float
    performance_level: str
    score: float
    unit: str
    comparison: str


class ESGAnalysis(BaseModel):
    company_name: str
    year: int
    metrics_analysis: Dict[str, MetricAnalysis]
    overall_score: float
    recommendations: List[str]


# Industry Benchmark schemas
class IndustryBenchmark(BaseModel):
    metric: str
    year: int
    statistics: Dict[str, float]
    companies: List[Dict[str, Any]]
    unit: str


# Health check schema
class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"
    database: str = "connected"
