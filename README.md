# EcoBench ESG Benchmarking Platform

A production-ready, enterprise-grade ESG benchmarking web application with AI-powered insights, built with FastAPI and React.js.

[![CI/CD Pipeline](https://github.com/ecobench/ecobench-platform/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/ecobench/ecobench-platform/actions)
[![Security Scan](https://github.com/ecobench/ecobench-platform/workflows/Security%20Scan/badge.svg)](https://github.com/ecobench/ecobench-platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### Core Functionality
- **📄 Document Ingestion**: Upload PDFs or provide URLs with intelligent text extraction and OCR fallback
- **🔍 KPI Extraction**: Hybrid regex + LLM extraction for comprehensive ESG metrics (Scope 1/2/3, water, waste, energy)
- **📊 Benchmarking**: Advanced peer group analysis with percentile rankings and industry comparisons
- **🤖 AI Guidance**: LLM-powered actionable recommendations for ESG improvement
- **🔎 Semantic Search**: Vector-based search across reports using pgvector for intelligent content discovery
- **📈 Dashboard**: Real-time ESG performance monitoring with interactive visualizations

### Technical Features
- **🎨 Modern UI**: React.js with Tailwind CSS, fully responsive design
- **🔐 Security**: JWT authentication, role-based access control, comprehensive audit logging
- **📡 Observability**: Prometheus metrics, structured logging, health checks
- **🚀 Performance**: Async processing, background jobs, optimized database queries
- **🔄 CI/CD**: Automated testing, security scanning, containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React.js      │◄──►│   FastAPI       │◄──►│  PostgreSQL     │
│   Tailwind CSS  │    │   Python 3.11   │    │   + pgvector    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   AI Services   │
                       │ TinyLlama/OpenAI│
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI with async/await support
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15 with pgvector extension
- **ORM**: SQLAlchemy 2.0 with Alembic migrations
- **AI/ML**: TinyLlama (local), OpenAI API, sentence-transformers
- **Processing**: PyPDF2, pdfminer, pytesseract for OCR
- **Monitoring**: Prometheus, structlog

### Frontend
- **Framework**: React.js 18 with Vite
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Context API + useReducer
- **Charts**: Chart.js for data visualization
- **HTTP Client**: Axios with interceptors
- **Icons**: Heroicons

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions with multi-stage workflows
- **Security**: CodeQL, Trivy, Safety, npm audit
- **Monitoring**: Prometheus + Grafana ready

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/ecobench-platform.git
cd ecobench-platform

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Generate sample data (optional)
docker-compose exec backend python scripts/generate_sample_data.py

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup (requires PostgreSQL with pgvector)
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Access at http://localhost:3000
```

## 📚 Documentation

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Monitoring & Health
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics (Prometheus format)
- **Application Logs**: Structured JSON logging with request tracing

### Development
- **Backend Tests**: `cd backend && pytest`
- **Frontend Tests**: `cd frontend && npm test`
- **Code Coverage**: `cd backend && pytest --cov=app`
- **Linting**: `cd backend && flake8 app tests`

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ecobench

# LLM Configuration
LLM_PROVIDER=mock  # Options: mock, tinyllama, openai
OPENAI_API_KEY=your_openai_api_key_here
TINYLLAMA_MODEL_PATH=/path/to/tinyllama/model

# Application
SECRET_KEY=your_secret_key_here
DEBUG=false
LOG_LEVEL=INFO

# File Storage
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads
```

#### Frontend
```bash
REACT_APP_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run with test database
pytest --tb=short -v
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## 🚢 Deployment

### Production Deployment

1. **Build Images**:
```bash
docker build -t ecobench-backend ./backend
docker build -t ecobench-frontend ./frontend
```

2. **Deploy with Docker Compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Database Migration**:
```bash
docker-compose exec backend alembic upgrade head
```

### CI/CD Pipeline

The project includes comprehensive GitHub Actions workflows:

- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Security Scanning**: CodeQL, dependency scanning, container scanning
- **PR Checks**: Code quality, test coverage, performance checks
- **Release Management**: Automated releases with semantic versioning

## 📊 Sample Data

Generate sample data for development and testing:

```bash
# Using Docker
docker-compose exec backend python scripts/generate_sample_data.py

# Local development
cd backend
python scripts/generate_sample_data.py
```

This creates:
- 5 sample organizations across different industries
- Sample users with different roles
- 10 KPI definitions covering E, S, and G metrics
- Historical KPI values for 3 years
- Sample reports and ingestion jobs
- Peer groups and benchmark snapshots
- AI-generated recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style and conventions
- Write tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` directory for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🙏 Acknowledgments

- Built with modern web technologies and best practices
- Inspired by the need for transparent ESG reporting and benchmarking
- Thanks to the open-source community for excellent tools and libraries

---

**EcoBench** - Empowering organizations with AI-driven ESG insights for a sustainable future.
