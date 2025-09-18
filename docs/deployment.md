# Deployment Guide

This guide covers deploying EcoBench in various environments from development to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Development Deployment](#development-deployment)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Database Management](#database-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: 2+ cores (4+ recommended for production)
- **RAM**: 4GB minimum (8GB+ recommended for production)
- **Storage**: 20GB minimum (100GB+ recommended for production)
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### Software Dependencies

- Docker 20.10+
- Docker Compose 2.0+
- Git
- PostgreSQL 15+ with pgvector extension
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## Environment Configuration

### Environment Files

Create environment files for each deployment stage:

#### Development (.env.dev)
```bash
# Database
DATABASE_URL=postgresql://ecobench_user:dev_password@localhost:5432/ecobench_dev

# Application
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key-change-in-production

# LLM
LLM_PROVIDER=mock
OPENAI_API_KEY=

# File Storage
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

#### Staging (.env.staging)
```bash
# Database
DATABASE_URL=postgresql://ecobench_user:staging_password@db:5432/ecobench_staging

# Application
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=staging-secret-key-use-strong-key

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=your_staging_openai_key

# File Storage
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=/app/uploads

# Frontend
REACT_APP_API_URL=https://api-staging.ecobench.com
```

#### Production (.env.prod)
```bash
# Database
DATABASE_URL=postgresql://ecobench_user:production_password@db:5432/ecobench_prod

# Application
DEBUG=false
LOG_LEVEL=WARNING
SECRET_KEY=production-secret-key-use-very-strong-key

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=your_production_openai_key

# File Storage
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=/app/uploads

# Frontend
REACT_APP_API_URL=https://api.ecobench.com

# Security
ALLOWED_HOSTS=api.ecobench.com,ecobench.com
CORS_ORIGINS=https://ecobench.com,https://www.ecobench.com
```

## Development Deployment

### Local Development with Docker Compose

```bash
# Clone repository
git clone https://github.com/your-org/ecobench-platform.git
cd ecobench-platform

# Copy and configure environment
cp .env.example .env
# Edit .env with your local settings

# Start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Generate sample data
docker-compose exec backend python scripts/generate_sample_data.py
```

### Local Development without Docker

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
createdb ecobench_dev
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## Staging Deployment

### Docker Compose for Staging

Create `docker-compose.staging.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://ecobench_user:${DB_PASSWORD}@db:5432/ecobench_staging
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_PROVIDER=openai
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_API_URL=https://api-staging.ecobench.com
    ports:
      - "80:3000"
    restart: unless-stopped

  db:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=ecobench_staging
      - POSTGRES_USER=ecobench_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

volumes:
  postgres_data:
  uploads_data:
```

Deploy to staging:

```bash
# Set environment variables
export DB_PASSWORD=your_staging_db_password
export SECRET_KEY=your_staging_secret_key
export OPENAI_API_KEY=your_openai_key

# Deploy
docker-compose -f docker-compose.staging.yml up -d

# Run migrations
docker-compose -f docker-compose.staging.yml exec backend alembic upgrade head

# Generate sample data
docker-compose -f docker-compose.staging.yml exec backend python scripts/generate_sample_data.py
```

## Production Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/your-org/ecobench-backend:latest
    environment:
      - DATABASE_URL=postgresql://ecobench_user:${DB_PASSWORD}@db:5432/ecobench_prod
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_PROVIDER=openai
      - DEBUG=false
      - LOG_LEVEL=WARNING
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - db
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  frontend:
    image: ghcr.io/your-org/ecobench-frontend:latest
    restart: unless-stopped
    deploy:
      replicas: 2

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  db:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=ecobench_prod
      - POSTGRES_USER=ecobench_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  uploads_data:
  prometheus_data:
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name ecobench.com www.ecobench.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name ecobench.com www.ecobench.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend docs
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend;
            access_log off;
        }

        # File uploads
        client_max_body_size 100M;
    }
}
```

### Production Deployment Steps

1. **Prepare Environment**:
```bash
# Set production environment variables
export DB_PASSWORD=$(openssl rand -base64 32)
export SECRET_KEY=$(openssl rand -base64 32)
export OPENAI_API_KEY=your_production_openai_key
export ALLOWED_HOSTS=api.ecobench.com,ecobench.com
export CORS_ORIGINS=https://ecobench.com,https://www.ecobench.com
```

2. **Deploy Application**:
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Deploy with zero downtime
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

3. **Verify Deployment**:
```bash
# Check service health
curl https://ecobench.com/health

# Check API documentation
curl https://ecobench.com/docs

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Database Management

### Backup and Restore

#### Backup
```bash
# Create backup
docker-compose exec db pg_dump -U ecobench_user ecobench_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker-compose exec db pg_dump -U ecobench_user ecobench_prod | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Restore
```bash
# Restore from backup
docker-compose exec -T db psql -U ecobench_user ecobench_prod < backup_20231201_120000.sql

# Restore from compressed backup
gunzip -c backup_20231201_120000.sql.gz | docker-compose exec -T db psql -U ecobench_user ecobench_prod
```

### Migrations

```bash
# Check current migration status
docker-compose exec backend alembic current

# Upgrade to latest
docker-compose exec backend alembic upgrade head

# Downgrade one revision
docker-compose exec backend alembic downgrade -1

# Show migration history
docker-compose exec backend alembic history
```

## Monitoring and Logging

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
docker-compose exec backend python -c "from app.database import test_connection; import asyncio; asyncio.run(test_connection())"

# Prometheus metrics
curl http://localhost:8000/metrics
```

### Log Management

```bash
# View application logs
docker-compose logs -f backend

# View specific service logs
docker-compose logs -f frontend

# Follow logs with timestamps
docker-compose logs -f -t backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Monitoring Setup

Access monitoring dashboards:

- **Prometheus**: http://localhost:9090
- **Application Metrics**: http://localhost:8000/metrics
- **Health Status**: http://localhost:8000/health

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database status
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec backend python -c "from app.database import test_connection; import asyncio; asyncio.run(test_connection())"
```

#### Frontend Build Issues
```bash
# Rebuild frontend
docker-compose build --no-cache frontend

# Check frontend logs
docker-compose logs frontend

# Access frontend container
docker-compose exec frontend sh
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check application metrics
curl http://localhost:8000/metrics | grep -E "(http_requests|response_time)"

# Monitor database performance
docker-compose exec db psql -U ecobench_user -d ecobench_prod -c "SELECT * FROM pg_stat_activity;"
```

### Recovery Procedures

#### Service Recovery
```bash
# Restart specific service
docker-compose restart backend

# Restart all services
docker-compose restart

# Force recreate containers
docker-compose up -d --force-recreate
```

#### Data Recovery
```bash
# Restore from backup
docker-compose exec -T db psql -U ecobench_user ecobench_prod < latest_backup.sql

# Reset to clean state
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/generate_sample_data.py
```

## Security Considerations

### SSL/TLS Configuration

1. **Obtain SSL Certificate**:
```bash
# Using Let's Encrypt
certbot certonly --webroot -w /var/www/html -d ecobench.com -d www.ecobench.com
```

2. **Configure Nginx**:
- Use strong SSL ciphers
- Enable HSTS
- Implement security headers

### Environment Security

1. **Secrets Management**:
- Use environment variables for sensitive data
- Never commit secrets to version control
- Rotate secrets regularly

2. **Network Security**:
- Use internal networks for service communication
- Implement firewall rules
- Regular security updates

### Backup Security

1. **Encrypt Backups**:
```bash
# Encrypted backup
docker-compose exec db pg_dump -U ecobench_user ecobench_prod | gpg --symmetric --cipher-algo AES256 > backup_encrypted.sql.gpg
```

2. **Secure Storage**:
- Store backups in secure, off-site locations
- Implement backup retention policies
- Test restore procedures regularly

This deployment guide provides comprehensive instructions for deploying EcoBench across different environments while maintaining security and reliability best practices.
