# IRIS v6.0 - Documentation Hub 📚

Welcome to the IRIS v6.0 documentation! This hub provides access to all project documentation.

## 🚀 Getting Started

**New to IRIS?** Start here:

1. **[Quickstart Guide](QUICKSTART.md)** - Get up and running in 5 minutes
2. **[Main README](../README.md)** - Complete project overview
3. **[API Documentation](http://localhost:8000/dokumentation)** - Interactive API docs (when server is running)

## 📖 Core Documentation

### User Guides

- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup and common tasks
- **[README.md](../README.md)** - Main project documentation with:
  - Architecture overview
  - Installation instructions
  - API examples
  - Configuration guide
  - Deployment guide

### Developer Guides

- **[CODING_GUIDELINES.md](../CODING_GUIDELINES.md)** - Code standards and best practices
  - Python style guide (PEP 8)
  - Naming conventions
  - Type hints requirements
  - Async/await patterns
  - Error handling
  - Logging standards
  - Security guidelines
  - AI/Windsurf Cascade workflows

- **[TESTING.md](../TESTING.md)** - Testing guide
  - Running tests
  - Writing tests
  - Test coverage
  - Fixtures and mocks
  - CI/CD integration

### Configuration Guides

- **[MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)** - AI model configuration
  - Model configuration system
  - `config/models.yaml` structure
  - Model Manager CLI usage
  - Adding custom models
  - Profile mappings
  - Fallback configuration
  - Integration examples

## 📝 Reference Documentation

### Project Management

- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes
  - Release notes
  - Breaking changes
  - New features
  - Bug fixes
  - Security updates

### Configuration Files

Located in `../config/`:
- **`models.yaml`** - AI model definitions
- **`profiles.yaml`** - AI profile configurations
- **`sources.yaml`** - Data source configurations

### Environment Setup

- **`.env.template`** - Environment variables template
  - Required API keys
  - Optional configurations
  - Security settings

## 🏗️ Architecture Documentation

### System Components

1. **Core Modules** (`src/core/`)
   - `config.py` - Configuration management
   - `model_config.py` - Model configuration manager
   - `database.py` - Database abstraction
   - `security.py` - Security and GDPR

2. **Services** (`src/services/`)
   - `ai_analyzer.py` - Multi-provider AI analysis
   - `profile_router.py` - Profile routing logic
   - `data_collector.py` - Data collection
   - `swedish_sources.py` - Swedish data sources
   - `ai_providers/` - Provider implementations

3. **Utilities** (`src/utils/`)
   - `model_manager_cli.py` - CLI tool
   - `error_handling.py` - Error handling utilities
   - `nlp_swedish.py` - Swedish NLP support

### AI Provider Architecture

```
┌─────────────────────────────────────┐
│      BaseAIProvider (Abstract)      │
└─────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
┌───────▼─────┐ ┌▼────────┐ ┌▼─────────┐
│ GroqProvider│ │XAIProvider│ │LocalProvider│
└─────────────┘ └─────────┘ └──────────┘
```

**Multi-Provider Fallback:**
```
Groq (Primary) → xAI (Fallback 1) → Local (Fallback 2)
```

## 🧪 Examples

### Code Examples

- **[examples/model_config_examples.py](../examples/model_config_examples.py)** - Model configuration usage examples

### API Examples

See [QUICKSTART.md](QUICKSTART.md#api-examples) for:
- Basic analysis
- Complex queries
- Streaming responses
- Profile selection

## 🔒 Security & GDPR

### Security Best Practices

From [CODING_GUIDELINES.md](../CODING_GUIDELINES.md#security):
- Never hardcode API keys
- Use environment variables
- Mask sensitive data in logs
- Follow GDPR compliance

### GDPR Compliance

IRIS v6.0 is GDPR-compliant by design:
- ✅ Consent management
- ✅ Data portability
- ✅ Right to be forgotten
- ✅ Transparent data processing
- ✅ Automatic PII protection

See `/gdpr/info` endpoint for user rights information.

## 📊 Testing

### Test Structure

```
tests/
├── test_api.py                          # API tests
├── test_model_config.py                 # Model config tests
├── test_ai_providers_comprehensive.py   # Provider tests
├── test_swedish_sources.py              # Source tests
└── conftest.py                         # Test fixtures
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_model_config.py -v
```

See [TESTING.md](../TESTING.md) for complete guide.

## 🛠️ CLI Tools

### Model Manager CLI

```bash
# List all models
python -m src.utils.model_manager_cli list

# Show model info
python -m src.utils.model_manager_cli info kimi-k2

# List profile models
python -m src.utils.model_manager_cli profile snabb

# Filter models
python -m src.utils.model_manager_cli list --provider groq --streaming
```

See [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md) for full CLI documentation.

## 🌐 API Documentation

When the server is running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/dokumentation
- **ReDoc**: http://localhost:8000/api-doc

### Main Endpoints

- `GET /` - Welcome message
- `POST /analysera` - Main analysis endpoint
- `GET /hälsa` - Health check
- `GET /profiler` - Available profiles
- `GET /datakällor` - Data sources
- `GET /gdpr/info` - GDPR information

## 📦 Dependencies

See `requirements.txt` for full dependency list.

**Key Dependencies:**
- FastAPI 0.115+ - Web framework
- Python 3.10+ - Programming language
- Groq SDK - Groq Cloud integration
- OpenAI SDK - xAI integration
- Redis - Caching
- PostgreSQL/SQLite - Database

## 🔄 Version History

See [CHANGELOG.md](../CHANGELOG.md) for detailed version history.

**Current Version:** 6.0.1
**Release Date:** 2025-11-06

## 🆘 Getting Help

### Documentation Issues

If you find documentation issues:
1. Check if information exists elsewhere
2. Report via GitHub Issues
3. Suggest improvements via Pull Request

### Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions
- **API Docs**: http://localhost:8000/dokumentation
- **Email**: support@iris.se (GDPR inquiries)

## 📁 Documentation Structure

```
docs/
├── README.md                    # This file
├── QUICKSTART.md               # Quick setup guide
├── MODEL_CONFIGURATION.md      # Model config guide
└── archive/                    # Archived documentation
    └── README.md              # Archive index

Root documentation:
├── README.md                   # Main project README
├── CHANGELOG.md               # Version history
├── CODING_GUIDELINES.md       # Code standards
├── TESTING.md                 # Testing guide
└── .env.template              # Environment template
```

## 🔗 External Resources

- **Python**: https://python.org
- **FastAPI**: https://fastapi.tiangolo.com
- **Docker**: https://docker.com
- **Groq Cloud**: https://console.groq.com
- **xAI**: https://x.ai
- **PEP 8**: https://pep8.org

## 🎯 Quick Links

| What | Where |
|------|-------|
| Get started quickly | [QUICKSTART.md](QUICKSTART.md) |
| Understand architecture | [README.md](../README.md#architecture) |
| Configure models | [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md) |
| Write code | [CODING_GUIDELINES.md](../CODING_GUIDELINES.md) |
| Run tests | [TESTING.md](../TESTING.md) |
| See changes | [CHANGELOG.md](../CHANGELOG.md) |
| Set up environment | [.env.template](../.env.template) |

---

## 🤝 Contributing to Documentation

When updating documentation:

1. **Accuracy**: Ensure information is current and correct
2. **Clarity**: Write clearly and concisely in svenska when appropriate
3. **Examples**: Include practical code examples
4. **Links**: Keep internal links up to date
5. **Consistency**: Follow existing documentation style
6. **Testing**: Test all code examples

---

**Last Updated:** 2025-11-06
**Documentation Version:** 1.0
**Project:** IRIS v6.0 - Intelligent Rapporteringssystem för Sverige 🇸🇪
