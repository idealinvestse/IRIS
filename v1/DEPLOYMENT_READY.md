# 🚀 IRIS v6.0 - Deployment Ready

**Status:** ✅ Production Ready  
**Date:** 2025-11-06  
**Version:** 6.0.1

---

## 📦 What's Included

Your IRIS v6.0 application is **fully containerized and ready for deployment** with:

### ✅ Docker Configuration
- **Dockerfile** - Multi-stage build (base, dependencies, development, production, test, lint)
- **docker-compose.yml** - Full production stack with PostgreSQL, Redis, Nginx, Prometheus, Grafana, Loki
- **docker-compose.dev.yml** - Development environment with hot reload
- **deploy.sh** - Automated deployment script

### ✅ Documentation
- **docs/DOCKER_DEPLOYMENT.md** - Comprehensive deployment guide (500+ lines)
- **docs/QUICKSTART.md** - 5-minute quick start guide
- **docs/README.md** - Documentation hub
- **CHANGELOG.md** - Version history
- **CODING_GUIDELINES.md** - Development standards

### ✅ Code Quality
- Type hints on all functions
- Comprehensive error handling
- Logging throughout
- Google-style docstrings
- GDPR-compliant architecture

### ✅ Features
- Multi-provider AI system (Groq, xAI, Local)
- Model configuration system
- Swedish data sources (SCB, OMX, SMHI, NewsData)
- Crawlee web scraping integration (POC)
- Monitoring & observability
- Database migrations
- Backup automation

---

## 🎯 Quick Deployment

### Development (< 5 minutes)

```bash
# Clone and setup
git clone https://github.com/idealinvestse/IRIS.git
cd IRIS/v1

# Copy environment
cp .env.template .env

# Deploy
./deploy.sh dev

# Access
# API: http://localhost:8000
# Docs: http://localhost:8000/dokumentation
```

### Production (< 10 minutes)

```bash
# Set environment variables
export POSTGRES_PASSWORD=your-secure-password
export SECRET_KEY=your-secret-key-32-chars
export XAI_API_KEY=your-xai-key
export GROQ_API_KEY=your-groq-key

# Deploy
./deploy.sh prod

# Access
# API: http://localhost:8000
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 IRIS v6.0 Stack                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend/API Layer:                                    │
│  ├─ Nginx (Reverse Proxy)                              │
│  └─ FastAPI (Gunicorn + Uvicorn)                       │
│                                                          │
│  Data Layer:                                            │
│  ├─ PostgreSQL (Primary Database)                      │
│  ├─ Redis (Cache)                                      │
│  └─ SQLite (Development)                               │
│                                                          │
│  Monitoring Layer:                                      │
│  ├─ Prometheus (Metrics)                               │
│  ├─ Grafana (Dashboards)                               │
│  └─ Loki (Logs)                                        │
│                                                          │
│  Services:                                              │
│  ├─ AI Analysis (Multi-provider)                       │
│  ├─ Data Collection (Crawlee)                          │
│  ├─ Swedish Sources (SCB, OMX, SMHI)                   │
│  └─ GDPR Compliance                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Required Environment Variables

```bash
# Database
POSTGRES_PASSWORD=secure-password

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
ENCRYPTION_KEY=your-encryption-key

# AI APIs
GROQ_API_KEY=gsk_your_groq_key
XAI_API_KEY=xai-your_xai_key

# Optional
NEWS_API_KEY=your_newsdata_key
GRAFANA_PASSWORD=admin-password
```

### Configuration Files

- `.env.template` - Environment template
- `config/models.yaml` - AI model definitions
- `config/profiles.yaml` - AI profile settings
- `config/sources.yaml` - Data source configuration

---

## 📈 Services

| Service | Port | Purpose | Dev | Prod |
|---------|------|---------|-----|------|
| **iris-app** | 8000 | Main API | ✅ | ✅ |
| **postgres** | 5432 | Database | ❌ | ✅ |
| **redis** | 6379 | Cache | ✅ | ✅ |
| **nginx** | 80/443 | Reverse Proxy | ❌ | ✅ |
| **prometheus** | 9090 | Metrics | ❌ | ✅ |
| **grafana** | 3000 | Dashboard | ❌ | ✅ |
| **loki** | 3100 | Logs | ❌ | ✅ |

---

## 🚀 Deployment Commands

### Using Deploy Script

```bash
# Development
./deploy.sh dev

# Production
./deploy.sh prod

# Testing
./deploy.sh test

# Code Quality
./deploy.sh lint

# Stop Services
./deploy.sh stop

# View Logs
./deploy.sh logs
```

### Using Docker Compose Directly

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker-compose --profile production up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f iris-app

# Rebuild
docker-compose build --no-cache
```

---

## 📊 Monitoring

### Grafana Dashboard
- **URL:** http://localhost:3000
- **Login:** admin / admin (or GRAFANA_PASSWORD)
- **Metrics:** CPU, Memory, Requests, Errors, Cache Hits

### Prometheus Metrics
- **URL:** http://localhost:9090
- **Metrics:** iris_requests_total, iris_request_duration_seconds, iris_errors_total

### Application Logs
```bash
docker-compose logs -f iris-app
```

---

## 🗄️ Database

### Backup
```bash
docker-compose exec backup sh /backup.sh
```

### Restore
```bash
docker-compose exec postgres psql -U iris -d iris < backups/iris_backup_YYYY-MM-DD.sql
```

### Migrations
```bash
docker-compose exec iris-app alembic upgrade head
```

---

## 🧪 Testing

### Run Tests
```bash
./deploy.sh test
```

### Code Quality
```bash
./deploy.sh lint
```

### Coverage Report
```bash
docker build -t iris:test --target test .
docker run --rm iris:test pytest tests/ -v --cov=src --cov-report=html
```

---

## 🔐 Security Checklist

- [ ] Environment variables set (not hardcoded)
- [ ] `.env` file in `.gitignore`
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Secrets management in place
- [ ] Network policies configured
- [ ] Resource limits set
- [ ] Health checks passing
- [ ] Monitoring dashboards created
- [ ] Log aggregation working

---

## 📚 Documentation

- **[DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)** - Complete Docker guide
- **[QUICKSTART.md](docs/QUICKSTART.md)** - 5-minute setup
- **[README.md](README.md)** - Project overview
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[CODING_GUIDELINES.md](CODING_GUIDELINES.md)** - Development standards

---

## 🎯 Next Steps

### 1. Prepare Environment
```bash
cp .env.template .env
# Edit .env with your values
```

### 2. Deploy
```bash
# Development
./deploy.sh dev

# Or Production
./deploy.sh prod
```

### 3. Verify
```bash
# Check health
curl http://localhost:8000/hälsa

# View logs
docker-compose logs -f iris-app

# Access API docs
open http://localhost:8000/dokumentation
```

### 4. Monitor
```bash
# Grafana dashboard
open http://localhost:3000

# Prometheus metrics
open http://localhost:9090
```

---

## 🆘 Troubleshooting

### Container Won't Start
```bash
docker-compose logs iris-app
docker-compose build --no-cache
```

### Database Connection Issues
```bash
docker-compose logs postgres
docker-compose exec postgres pg_isready -U iris
```

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different port
```

### Memory Issues
```bash
# Check resource usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Preferences > Resources > Memory
```

---

## 📞 Support

For issues or questions:

1. **Check Logs:** `docker-compose logs -f`
2. **Review Docs:** `docs/DOCKER_DEPLOYMENT.md`
3. **Report Issues:** GitHub Issues
4. **Contact:** support@iris.se

---

## ✅ Deployment Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Database backups working
- [ ] SSL certificates installed
- [ ] Monitoring dashboards created
- [ ] Health checks passing
- [ ] Resource limits set
- [ ] Network policies configured
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations
- [ ] Runbook created

---

## 🎉 You're Ready!

Your IRIS v6.0 application is **production-ready** and can be deployed with a single command:

```bash
./deploy.sh prod
```

**Happy deploying! 🚀🇸🇪**

---

**IRIS v6.0** | Förenklad och Robust Intelligensrapportering för Sverige  
**Deployment Ready** | 2025-11-06
