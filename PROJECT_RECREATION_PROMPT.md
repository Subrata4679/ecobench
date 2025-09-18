# EcoBench ESG Platform - Complete Recreation Prompt

## Overview
This prompt will recreate a complete, production-ready ESG (Environmental, Social, Governance) benchmarking platform with AI-powered insights. The application includes a React.js frontend, FastAPI backend, PostgreSQL database with vector search, and comprehensive Docker setup.

## Project Structure to Create
```
windsurf-project/
├── frontend/                 # React.js application
├── backend/                  # FastAPI Python application
├── docs/                     # Documentation
├── .github/workflows/        # CI/CD pipelines
├── docker-compose.yml        # Docker orchestration
├── .env.example             # Environment template
├── README.md                # Project documentation
└── prometheus.yml           # Monitoring configuration
```

## Step-by-Step Instructions

### 1. Initial Setup
Create a new directory and initialize the project:
```bash
mkdir windsurf-project
cd windsurf-project
```

### 2. Request the AI Assistant
Use this exact prompt with your AI assistant:

---

**PROMPT START:**

Create a complete, production-ready ESG (Environmental, Social, Governance) benchmarking web application called "EcoBench" with the following specifications:

## Core Features Required:
1. **Document Ingestion**: PDF upload and URL processing with OCR fallback
2. **KPI Extraction**: Extract ESG metrics (Scope 1/2/3 emissions, water, waste, energy) using hybrid regex + LLM
3. **Benchmarking**: Peer group analysis with percentile rankings and industry comparisons
4. **AI Guidance**: LLM-powered actionable recommendations for ESG improvement
5. **Semantic Search**: Vector-based search across reports using pgvector
6. **Dashboard**: Real-time ESG performance monitoring with interactive charts

## Technical Stack:
### Backend:
- FastAPI with Python 3.11+
- PostgreSQL 15 with pgvector extension
- SQLAlchemy 2.0 with Alembic migrations
- JWT authentication with role-based access
- Prometheus metrics and structured logging
- AI/ML: Support for TinyLlama (local) and OpenAI API
- Document processing: PyPDF2, pdfminer, pytesseract for OCR
- Background jobs with Celery and Redis

### Frontend:
- React.js 18 with modern hooks
- Tailwind CSS for styling
- Chart.js and Recharts for data visualization
- Axios for API communication
- React Router for navigation
- Zustand for state management
- Responsive design with modern UI/UX

### Infrastructure:
- Docker and Docker Compose for containerization
- GitHub Actions for CI/CD
- Security scanning (CodeQL, Trivy, Safety)
- Prometheus monitoring setup
- Health checks and observability

## Specific Requirements:

### 1. Backend Structure:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # Settings and configuration
│   │   ├── security.py      # JWT and authentication
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── kpi.py
│   │   ├── report.py
│   │   └── benchmark.py
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organizations.py
│   │   ├── kpis.py
│   │   ├── reports.py
│   │   ├── benchmarks.py
│   │   └── search.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── document_processor.py
│   │   ├── kpi_extractor.py
│   │   ├── benchmark_service.py
│   │   ├── llm_service.py
│   │   └── search_service.py
│   └── utils/               # Utilities
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container definition
```

### 2. Frontend Structure:
```
frontend/
├── public/
├── src/
│   ├── components/          # Reusable components
│   │   ├── common/         # Common UI components
│   │   ├── charts/         # Chart components
│   │   ├── forms/          # Form components
│   │   └── layout/         # Layout components
│   ├── pages/              # Page components
│   │   ├── Dashboard.js
│   │   ├── Organizations.js
│   │   ├── Reports.js
│   │   ├── Benchmarks.js
│   │   └── Search.js
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── store/              # State management
│   ├── utils/              # Utilities
│   ├── styles/             # CSS and Tailwind config
│   ├── App.js              # Main app component
│   └── index.js            # Entry point
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
└── Dockerfile             # Container definition
```

### 3. Key Models and Schemas:
- **User**: Authentication, roles (admin, analyst, viewer)
- **Organization**: Company profiles with industry classification
- **KPI**: ESG metrics with definitions, units, calculation methods
- **Report**: Document metadata, processing status, extracted content
- **KPIValue**: Historical ESG data points with validation
- **Benchmark**: Peer group comparisons and percentile rankings
- **Recommendation**: AI-generated improvement suggestions

### 4. API Endpoints:
- Authentication: `/auth/login`, `/auth/register`, `/auth/refresh`
- Organizations: CRUD operations with filtering and search
- Reports: Upload, processing status, content extraction
- KPIs: Definitions, values, historical trends
- Benchmarks: Peer analysis, industry comparisons
- Search: Semantic search across all content
- Dashboard: Aggregated metrics and insights

### 5. Features to Implement:
- File upload with drag-and-drop interface
- Real-time processing status updates
- Interactive charts and data visualizations
- Advanced filtering and search capabilities
- Export functionality (PDF, Excel, CSV)
- User management and role-based permissions
- Audit logging and activity tracking
- Responsive design for mobile and desktop

### 6. Sample Data:
Create comprehensive sample data including:
- 5 organizations across different industries (Tech, Manufacturing, Energy, Finance, Retail)
- 10+ KPI definitions covering E, S, and G metrics
- Historical data for 3 years
- Sample reports and processing results
- Benchmark data and peer groups
- AI-generated recommendations

### 7. Configuration:
- Environment-based configuration
- Docker Compose for development and production
- Database migrations with Alembic
- Comprehensive testing setup
- CI/CD pipeline with GitHub Actions
- Security scanning and code quality checks

### 8. Documentation:
- Comprehensive README with setup instructions
- API documentation with Swagger/OpenAPI
- Development guidelines and contribution guide
- Deployment instructions
- Architecture documentation

## Important Notes:
1. Use modern Python and JavaScript practices
2. Implement proper error handling and validation
3. Add comprehensive logging and monitoring
4. Ensure security best practices (JWT, CORS, input validation)
5. Make the UI beautiful and user-friendly with Tailwind CSS
6. Include proper testing setup for both frontend and backend
7. Add health checks and observability features
8. Support both local development and containerized deployment

Create the complete, working application with all files, configurations, and documentation. Make it production-ready with proper error handling, security, and monitoring.

**PROMPT END:**

---

### 3. After AI Creates the Project

Once the AI has created all the files, run these commands to set up and start the application:

```bash
# Copy environment configuration
cp .env.example .env

# Edit .env file with your settings (database credentials, API keys, etc.)

# Start the application with Docker
docker-compose up -d

# Generate sample data (optional)
docker-compose exec backend python scripts/generate_sample_data.py

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 4. For Local Development (Alternative)

If you prefer local development without Docker:

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up PostgreSQL database with pgvector extension
# Update DATABASE_URL in .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm start

# Access at http://localhost:3000
```

## Expected Result

You will get a complete, production-ready ESG benchmarking platform with:

- **Modern React.js frontend** with Tailwind CSS styling
- **FastAPI backend** with comprehensive API endpoints
- **PostgreSQL database** with vector search capabilities
- **AI-powered features** for document processing and recommendations
- **Interactive dashboards** with charts and data visualizations
- **Docker containerization** for easy deployment
- **CI/CD pipeline** with GitHub Actions
- **Comprehensive documentation** and setup guides
- **Sample data** for immediate testing and demonstration

The application will be fully functional and ready for customization or deployment.

## Key Features You'll Have:

1. **Document Upload**: Drag-and-drop PDF upload with processing status
2. **ESG Metrics Dashboard**: Interactive charts showing environmental, social, and governance metrics
3. **Benchmarking**: Compare your organization against industry peers
4. **AI Recommendations**: Get actionable insights for ESG improvement
5. **Search**: Semantic search across all uploaded documents and data
6. **User Management**: Role-based access control with different permission levels
7. **Export Capabilities**: Download reports in various formats
8. **Real-time Updates**: Live status updates during document processing
9. **Responsive Design**: Works perfectly on desktop, tablet, and mobile
10. **Production Ready**: Includes monitoring, logging, security, and deployment configurations

This prompt will recreate the exact same comprehensive ESG platform that was built in this session.
