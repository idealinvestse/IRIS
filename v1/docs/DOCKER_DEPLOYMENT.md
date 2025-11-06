# Docker Deployment Guide for IRIS v6.0

**Version:** 1.0  
**Date:** 2025-11-06  
**Status:** Production Ready

## 📋 Overview

IRIS v6.0 is fully containerized with Docker and Docker Compose for easy deployment across different environments:

- **Development**: Hot reload with SQLite
- **Production**: PostgreSQL, Redis, Nginx, Monitoring
- **Testing**: Isolated test environment
- **CI/CD**: Automated testing and linting

## 🚀 Quick Start (5 minutes)

### Prerequisites

```bash
# Install Docker and Docker Compose
# macOS/Windows: Download Docker Desktop
# Linux: sudo apt-get install docker.io docker-compose
```

### Development Mode

```bash
# Clone repository
git clone https://github.com/idealinvestse/IRIS.git
cd IRIS/v1

# Copy environment template
cp .env.template .env

# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f iris-app

# Access application
# API: http://localhost:8000
# Docs: http://localhost:8000/dokumentation
```

### Production Mode

```bash
# Set environment variables
export POSTGRES_PASSWORD=your-secure-password
export SECRET_KEY=your-secret-key
export XAI_API_KEY=your-xai-key
export GROQ_API_KEY=your-groq-key

# Start production environment
docker-compose --profile production up -d

# View logs
docker-compose logs -f iris-app

# Access services
# API: http://localhost:8000
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 🏗️ Architecture

### Services

```
┌─────────────────────────────────────────────────────────┐
│                    IRIS v6.0 Stack                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Nginx      │  │  Prometheus  │  │   Grafana    │  │
│  │ (Reverse     │  │ (Metrics)    │  │ (Dashboard)  │  │
│  │  Proxy)      │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │          IRIS FastAPI Application                │  │
│  │  (Gunicorn + Uvicorn Workers)                    │  │
│  └──────────────────────────────────────────────────┘  │
│         │                    │                          │
│         ▼                    ▼                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │    Redis     │  │    Loki      │  │
│  │ (Database)   │  │   (Cache)    │  │   (Logs)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Services Details

| Service | Port | Purpose | Dev | Prod |
|---------|------|---------|-----|------|
| **iris-app** | 8000 | Main API | ✅ | ✅ |
| **postgres** | 5432 | Database | ❌ | ✅ |
| **redis** | 6379 | Cache | ✅ | ✅ |
| **nginx** | 80/443 | Reverse Proxy | ❌ | ✅ |
| **prometheus** | 9090 | Metrics | ❌ | ✅ |
| **grafana** | 3000 | Dashboard | ❌ | ✅ |
| **loki** | 3100 | Logs | ❌ | ✅ |

## 📦 Docker Images

### Build Stages

The Dockerfile uses multi-stage builds for optimization:

```dockerfile
# Stage 1: base
# - Python 3.12 slim
# - System dependencies
# - Swedish locale

# Stage 2: dependencies
# - Python packages from requirements.txt
# - spaCy Swedish models

# Stage 3: development
# - Dev tools (pytest, black, mypy, etc.)
# - Hot reload enabled

# Stage 4: production
# - Optimized for production
# - Gunicorn + Uvicorn workers
# - Health checks

# Stage 5: test
# - Test environment
# - pytest, coverage

# Stage 6: lint
# - Code quality checks
# - black, isort, mypy, flake8, bandit
```

### Build Commands

```bash
# Build production image
docker build -t iris:latest --target production .

# Build development image
docker build -t iris:dev --target development .

# Build test image
docker build -t iris:test --target test .

# Build lint image
docker build -t iris:lint --target lint .
```

## 🔧 Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.template .env
```

**Required for Production:**

```bash
# Database
POSTGRES_PASSWORD=secure-password-here

# Security
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-encryption-key

# AI APIs
GROQ_API_KEY=gsk_your_groq_key
XAI_API_KEY=xai-your_xai_key

# Optional
NEWS_API_KEY=your_newsdata_key
GRAFANA_PASSWORD=admin-password
```

### Docker Compose Overrides

**Development:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production:**
```bash
docker-compose --profile production up -d
```

## 📊 Monitoring & Logs

### Grafana Dashboard

1. Access: http://localhost:3000
2. Login: admin / admin (or GRAFANA_PASSWORD)
3. Add Prometheus datasource: http://prometheus:9090
4. Import dashboards from `docker/grafana/dashboards/`

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f iris-app

# Last 100 lines
docker-compose logs --tail=100 iris-app

# With timestamps
docker-compose logs -f --timestamps iris-app
```

### Prometheus Metrics

Access: http://localhost:9090

**Key Metrics:**
- `iris_requests_total` - Total API requests
- `iris_request_duration_seconds` - Request latency
- `iris_errors_total` - Error count
- `iris_cache_hits_total` - Cache hits
- `iris_db_connections` - Database connections

## 🗄️ Database Management

### Backup Database

```bash
# Manual backup
docker-compose exec backup sh /backup.sh

# View backups
ls -la backups/

# Restore from backup
docker-compose exec postgres psql -U iris -d iris < backups/iris_backup_YYYY-MM-DD.sql
```

### Database Migrations

```bash
# Run migrations
docker-compose exec iris-app alembic upgrade head

# Create new migration
docker-compose exec iris-app alembic revision --autogenerate -m "Description"

# Downgrade
docker-compose exec iris-app alembic downgrade -1
```

### Access Database

```bash
# PostgreSQL CLI
docker-compose exec postgres psql -U iris -d iris

# Redis CLI
docker-compose exec redis redis-cli
```

## 🧪 Testing

### Run Tests

```bash
# Build test image
docker build -t iris:test --target test .

# Run tests
docker run --rm iris:test

# Run with coverage
docker run --rm iris:test pytest tests/ -v --cov=src --cov-report=html
```

### Code Quality

```bash
# Build lint image
docker build -t iris:lint --target lint .

# Run linting
docker run --rm iris:lint
```

## 🔐 Security Best Practices

### 1. Environment Variables

✅ **DO:**
```bash
# Use .env file (not committed)
export GROQ_API_KEY=$(cat .env | grep GROQ_API_KEY | cut -d '=' -f2)

# Use Docker secrets (Swarm)
docker secret create groq_key -
```

❌ **DON'T:**
```bash
# Don't hardcode in Dockerfile
ENV GROQ_API_KEY=gsk_...

# Don't pass on command line
docker run -e GROQ_API_KEY=gsk_...
```

### 2. Container Security

```bash
# Run as non-root user (already configured)
USER iris

# Read-only filesystems where possible
volumes:
  - ./config:/app/config:ro

# Resource limits
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### 3. Network Security

```bash
# Use internal network
networks:
  iris-network:
    driver: bridge

# Expose only necessary ports
ports:
  - "8000:8000"  # API only
  # Don't expose: 5432, 6379, 9090, 3000
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale API instances (with load balancer)
docker-compose up -d --scale iris-app=3
```

### Vertical Scaling

Update `docker-compose.yml`:

```yaml
iris-app:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
      reservations:
        cpus: '2'
        memory: 2G
```

## 🚨 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs iris-app

# Inspect container
docker inspect iris-v6-app

# Rebuild image
docker-compose build --no-cache iris-app
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready -U iris

# Reset database
docker-compose down -v  # WARNING: Deletes data!
docker-compose up -d
```

### Memory Issues

```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# Docker Desktop: Preferences > Resources > Memory

# Or in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different port
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build & Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t iris:latest --target production .
      
      - name: Run tests
        run: docker build -t iris:test --target test . && docker run --rm iris:test
      
      - name: Push to registry
        run: docker push iris:latest
```

## 📚 Additional Resources

- **Docker Docs**: https://docs.docker.com
- **Docker Compose**: https://docs.docker.com/compose
- **PostgreSQL**: https://www.postgresql.org/docs
- **Redis**: https://redis.io/documentation
- **Prometheus**: https://prometheus.io/docs
- **Grafana**: https://grafana.com/docs

## 🎯 Deployment Checklist

Before deploying to production:

- [ ] All environment variables set
- [ ] Database backups configured
- [ ] SSL certificates installed
- [ ] Monitoring dashboards created
- [ ] Log aggregation working
- [ ] Health checks passing
- [ ] Resource limits set
- [ ] Network policies configured
- [ ] Secrets management in place
- [ ] Disaster recovery plan documented

## 🆘 Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review documentation: `docs/DOCKER_DEPLOYMENT.md`
3. Report issues: GitHub Issues
4. Contact support: support@iris.se

---

**IRIS v6.0 Docker Deployment** | Production Ready | 2025-11-06
