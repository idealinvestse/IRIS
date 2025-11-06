# IRIS v6.0 - Quickstart Guide 🚀

Get IRIS up and running in under 5 minutes!

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Python 3.10+** (for local development)
- **Git**
- At least **2GB RAM**
- **Internet connection** (för externa API:er)

## ⚡ Quick Setup (5 minuter)

### 1. Clone Repository

```bash
git clone https://github.com/idealinvestse/IRIS.git
cd IRIS/v1
```

### 2. Configure Environment

```bash
# Copy template file
cp .env.template .env

# Edit with your favorite editor
nano .env  # or vim, code, notepad, etc.
```

**Required API Keys:**

```bash
# Get from: https://console.groq.com
GROQ_API_KEY=gsk_your_groq_api_key_here

# Get from: https://x.ai
XAI_API_KEY=xai-your_xai_api_key_here

# Security (generate random string)
SECRET_KEY=your-secret-key-minimum-32-characters
```

**Optional API Keys:**

```bash
# For Swedish news (Get from: https://newsdata.io)
NEWS_API_KEY=pub_your_newsdata_key_here
```

### 3. Start with Docker (Recommended)

```bash
# Development mode with SQLite
docker-compose up -d

# Or production mode with PostgreSQL
docker-compose --profile production up -d
```

**Wait for services to start (~30 seconds)**

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/hälsa

# Expected response:
# {"status":"frisk","tidsstämpel":"...","tjänster":{...}}
```

### 5. Test AI Analysis

```bash
# Simple query with fast profile
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Vad är 2+2?",
    "profil": "snabb"
  }'
```

**🎉 Congratulations! IRIS is now running!**

---

## 🛠️ Local Development Setup

If you prefer to run without Docker:

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Swedish NLP Models

```bash
python -m spacy download sv_core_news_sm
```

### 4. Start Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Redis (Optional, for caching)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally and run
redis-server
```

---

## 📚 Common Tasks

### View Available Profiles

```bash
curl http://localhost:8000/profiler
```

**Available Profiles:**
- **snabb**: Fast responses (< 2s) with Groq Kimi K2
- **smart**: Balanced analysis (3-7s) with xAI Grok
- **privat**: Local processing (5-15s), no external APIs

### List AI Models

```bash
python -m src.utils.model_manager_cli list
```

### Get Model Information

```bash
python -m src.utils.model_manager_cli info kimi-k2
```

### Check Available Data Sources

```bash
curl http://localhost:8000/datakällor
```

**Swedish Sources:**
- **SCB**: Statistiska centralbyrån
- **OMX**: Stockholm Stock Exchange
- **SMHI**: Weather data
- **NewsData**: Swedish news

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Test Specific Provider

```bash
# Model configuration tests
pytest tests/test_model_config.py -v

# AI provider tests
pytest tests/test_ai_providers_comprehensive.py -v
```

---

## 🔧 Configuration

### Model Configuration

Edit `config/models.yaml` to add or modify AI models:

```yaml
ai_models:
  my-custom-model:
    namn: "My Custom Model"
    provider: "groq"
    model_id: "custom-model-id"
    max_tokens: 4096
    default_temperature: 0.7
    supports_streaming: true
```

### Profile Configuration

Edit `config/profiles.yaml` to customize AI profiles:

```yaml
snabb:
  ai_provider: "groq"
  ai_model: "moonshotai/kimi-k2-instruct-0905"
  temperature: 0.6
  max_tokens: 2048
  streaming: true
```

### Source Configuration

Edit `config/sources.yaml` to add Swedish data sources:

```yaml
scb:
  url: "https://api.scb.se/OV0104/v1/doris/sv/ssd/"
  cache_ttl: 3600
  enabled: true
```

---

## 📖 API Examples

### Basic Analysis

```bash
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hur är vädret i Stockholm?",
    "profil": "snabb"
  }'
```

### Complex Analysis with Multiple Sources

```bash
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analysera svenska ekonomin baserat på OMX och SCB-data",
    "profil": "smart"
  }'
```

### Private Analysis (No External APIs)

```bash
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Sammanfatta denna information lokalt",
    "profil": "privat"
  }'
```

### Streaming Response

```python
import asyncio
from src.services.ai_providers.groq_provider import GroqProvider

async def stream_example():
    provider = GroqProvider(api_key="your-key")
    async for chunk in provider.analyze_stream(
        query="Räkna till 10",
        context="",
        model="moonshotai/kimi-k2-instruct-0905"
    ):
        print(chunk, end="", flush=True)

asyncio.run(stream_example())
```

---

## 🌐 Access Points

Once running, access these URLs:

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/dokumentation
- **ReDoc API Docs**: http://localhost:8000/api-doc
- **Health Check**: http://localhost:8000/hälsa
- **Grafana** (production): http://localhost:3000 (admin/admin)
- **Prometheus** (production): http://localhost:9090

---

## 🐛 Troubleshooting

### Issue: "Connection refused"

**Solution:** Ensure Docker is running and services are up:
```bash
docker-compose ps
docker-compose logs iris-app
```

### Issue: "API key missing"

**Solution:** Check your `.env` file:
```bash
cat .env | grep API_KEY
# Ensure GROQ_API_KEY and/or XAI_API_KEY are set
```

### Issue: "Module not found"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:** Stop existing service or use different port:
```bash
# Find process using port 8000
lsof -i :8000  # Unix/Mac
netstat -ano | findstr :8000  # Windows

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Issue: "Slow responses"

**Solutions:**
1. Check Redis is running for caching
2. Verify API keys are valid
3. Use "snabb" profile for faster responses
4. Check external API rate limits

---

## 📚 Next Steps

1. **Read Full Documentation**: See [README.md](../README.md)
2. **Model Configuration**: Read [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)
3. **Coding Guidelines**: Check [CODING_GUIDELINES.md](../CODING_GUIDELINES.md)
4. **Testing Guide**: Review [TESTING.md](../TESTING.md)
5. **API Documentation**: Explore http://localhost:8000/dokumentation

---

## 🆘 Getting Help

- **Issues**: Report bugs at GitHub Issues
- **Documentation**: Browse `/docs` folder
- **API Docs**: http://localhost:8000/dokumentation
- **GDPR Questions**: See `/gdpr/info` endpoint

---

## ✅ Quick Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f iris-app

# Restart service
docker-compose restart iris-app

# Run tests
pytest tests/ -v

# List models
python -m src.utils.model_manager_cli list

# Check health
curl http://localhost:8000/hälsa
```

---

**🇸🇪 Happy coding with IRIS v6.0!**

För mer information, se [README.md](../README.md) eller besök [dokumentationen](http://localhost:8000/dokumentation).
