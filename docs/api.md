# API Documentation

This document provides comprehensive documentation for the EcoBench API endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.ecobench.com`

## Authentication

EcoBench uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

#### POST /api/auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "analyst"
  }
}
```

#### GET /api/auth/me
Get current user information.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "analyst",
  "organization_id": 1,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

## Organizations

### GET /api/organizations
List all organizations with optional filtering.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100)
- `search` (string): Search term for organization name
- `industry` (string): Filter by industry
- `size` (string): Filter by organization size

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "TechCorp Industries",
      "industry": "Technology",
      "size": "Large",
      "description": "Leading technology company",
      "website": "https://techcorp.example.com",
      "headquarters": "San Francisco, CA",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### POST /api/organizations
Create a new organization.

**Request Body:**
```json
{
  "name": "New Organization",
  "industry": "Technology",
  "size": "Medium",
  "description": "Organization description",
  "website": "https://example.com",
  "headquarters": "New York, NY"
}
```

### GET /api/organizations/{id}
Get organization by ID.

### PUT /api/organizations/{id}
Update organization.

### DELETE /api/organizations/{id}
Delete organization.

### GET /api/organizations/stats
Get organization statistics.

**Response:**
```json
{
  "total_organizations": 25,
  "by_industry": {
    "Technology": 10,
    "Energy": 8,
    "Manufacturing": 7
  },
  "by_size": {
    "Large": 15,
    "Medium": 8,
    "Small": 2
  }
}
```

## Reports

### GET /api/reports
List reports with filtering options.

**Query Parameters:**
- `skip`, `limit`: Pagination
- `organization_id` (int): Filter by organization
- `file_type` (string): Filter by file type
- `search` (string): Search in title and description

### POST /api/reports/upload
Upload a new report file.

**Request:** Multipart form data
- `file`: PDF file
- `title`: Report title
- `description`: Report description
- `organization_id`: Organization ID

**Response:**
```json
{
  "id": 1,
  "title": "2023 Sustainability Report",
  "file_type": "pdf",
  "file_size": 2048000,
  "file_path": "/uploads/report_123.pdf",
  "organization_id": 1,
  "uploaded_by": 1,
  "upload_date": "2023-12-01T10:00:00Z"
}
```

### POST /api/reports/fetch-url
Fetch report from URL.

**Request Body:**
```json
{
  "url": "https://example.com/report.pdf",
  "title": "External Report",
  "description": "Report from external source",
  "organization_id": 1
}
```

### GET /api/reports/{id}/chunks
Get text chunks from processed report.

**Response:**
```json
{
  "chunks": [
    {
      "id": 1,
      "content": "This section covers our carbon emissions...",
      "page_number": 1,
      "chunk_index": 0
    }
  ]
}
```

### POST /api/reports/{id}/extract-kpis
Trigger KPI extraction for a report.

## KPIs

### GET /api/kpis/definitions
List KPI definitions.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Carbon Emissions (Scope 1)",
      "description": "Direct greenhouse gas emissions",
      "category": "Environmental",
      "unit": "tCO2e",
      "data_type": "numeric"
    }
  ]
}
```

### POST /api/kpis/definitions
Create new KPI definition.

### GET /api/kpis/values
List KPI values with filtering.

**Query Parameters:**
- `organization_id` (int): Filter by organization
- `kpi_definition_id` (int): Filter by KPI definition
- `reporting_period` (string): Filter by reporting period
- `category` (string): Filter by KPI category

### POST /api/kpis/values
Create new KPI value.

**Request Body:**
```json
{
  "kpi_definition_id": 1,
  "organization_id": 1,
  "value": "1250.5",
  "reporting_period": "2023-12-31",
  "data_source": "Annual Report 2023",
  "confidence_score": 0.95
}
```

## Ingestion

### GET /api/ingestion/jobs
List ingestion jobs.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "report_id": 1,
      "job_type": "pdf_processing",
      "status": "completed",
      "started_at": "2023-12-01T10:00:00Z",
      "completed_at": "2023-12-01T10:05:00Z",
      "result": {
        "processed_pages": 45,
        "extracted_text_length": 125000
      }
    }
  ]
}
```

### POST /api/ingestion/jobs
Create new ingestion job.

### POST /api/ingestion/jobs/{id}/run
Run ingestion job.

### DELETE /api/ingestion/jobs/{id}
Delete ingestion job.

### GET /api/ingestion/available-reports
Get reports available for ingestion.

## Benchmarks

### GET /api/benchmarks/snapshots
List benchmark snapshots.

### POST /api/benchmarks/snapshots
Create benchmark snapshot.

### GET /api/benchmarks/peer-groups
List peer groups.

### POST /api/benchmarks/peer-groups
Create peer group.

**Request Body:**
```json
{
  "name": "Technology Peer Group",
  "description": "Companies in technology sector",
  "criteria": {
    "industry": "Technology",
    "size": "Large"
  },
  "organization_ids": [1, 2, 3]
}
```

### GET /api/benchmarks/latest/{organization_id}
Get latest benchmark results for organization.

**Response:**
```json
{
  "organization_id": 1,
  "benchmark_date": "2023-12-01T00:00:00Z",
  "metrics": {
    "esg_score": 85.5,
    "environmental_score": 82.0,
    "social_score": 88.0,
    "governance_score": 87.0,
    "peer_rank": 3,
    "industry_percentile": 75.5
  },
  "peer_comparison": {
    "better_than": 65.0,
    "similar_to": 25.0,
    "worse_than": 10.0
  }
}
```

## Recommendations

### GET /api/recommendations
List recommendations with filtering.

**Query Parameters:**
- `organization_id` (int): Filter by organization
- `category` (string): Filter by category (Environmental, Social, Governance)
- `priority` (string): Filter by priority (high, medium, low)
- `status` (string): Filter by status (pending, in_progress, completed)

### POST /api/recommendations
Create new recommendation.

### POST /api/recommendations/generate
Generate AI recommendations for organization.

**Request Body:**
```json
{
  "organization_id": 1,
  "focus_areas": ["carbon_emissions", "waste_management"],
  "analysis_depth": "detailed"
}
```

### PUT /api/recommendations/{id}/status
Update recommendation status.

**Request Body:**
```json
{
  "status": "in_progress",
  "notes": "Implementation started"
}
```

## Search

### POST /api/search/semantic
Perform semantic search across reports.

**Request Body:**
```json
{
  "query": "carbon emissions reduction strategies",
  "organization_ids": [1, 2],
  "limit": 10,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "chunk_id": 1,
      "content": "Our carbon reduction strategy focuses on...",
      "similarity_score": 0.92,
      "report": {
        "id": 1,
        "title": "2023 Sustainability Report",
        "organization": {
          "id": 1,
          "name": "TechCorp Industries"
        }
      },
      "page_number": 15
    }
  ],
  "total_results": 25,
  "query_time_ms": 45
}
```

### GET /api/search/suggestions
Get search suggestions based on query.

**Query Parameters:**
- `q` (string): Partial query for suggestions

**Response:**
```json
{
  "suggestions": [
    "carbon emissions",
    "carbon footprint",
    "carbon reduction"
  ]
}
```

## Health and Monitoring

### GET /health
Application health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-01T10:00:00Z",
  "version": "1.0.0",
  "service": "ecobench-api"
}
```

### GET /metrics
Prometheus metrics endpoint (text/plain format).

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": {
    "field": "email",
    "issue": "Invalid email format"
  },
  "request_id": "req_123456789"
}
```

### Common Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

API requests are rate limited:
- **Authenticated users**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```
GET /api/organizations?skip=20&limit=10
```

Response includes pagination metadata:
```json
{
  "items": [...],
  "total": 150,
  "skip": 20,
  "limit": 10,
  "has_next": true,
  "has_prev": true
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

```
GET /api/reports?organization_id=1&file_type=pdf&sort=upload_date&order=desc
```

## Bulk Operations

Some endpoints support bulk operations:

### POST /api/kpis/values/bulk
Create multiple KPI values.

**Request Body:**
```json
{
  "values": [
    {
      "kpi_definition_id": 1,
      "organization_id": 1,
      "value": "1250.5",
      "reporting_period": "2023-12-31"
    },
    {
      "kpi_definition_id": 2,
      "organization_id": 1,
      "value": "850.2",
      "reporting_period": "2023-12-31"
    }
  ]
}
```

## WebSocket Endpoints

Real-time updates for long-running operations:

### WS /api/ws/ingestion/{job_id}
Real-time ingestion job progress updates.

**Message Format:**
```json
{
  "type": "progress",
  "job_id": 1,
  "status": "processing",
  "progress": 45,
  "message": "Processing page 15 of 33"
}
```

This API documentation provides comprehensive coverage of all EcoBench endpoints with examples and detailed specifications.
