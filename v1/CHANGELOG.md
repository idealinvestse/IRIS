# Changelog

All notable changes to IRIS v6.0 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Implemented comprehensive `.gitignore` to prevent accidental commits of sensitive files
- Created `.env.template` for safe environment variable distribution
- Removed all API keys from git history by creating clean repository
- Added security guidelines in `CODING_GUIDELINES.md`

## [6.0.1] - 2025-11-06

### Added
- **Model Configuration System**: Centralized AI model management via `config/models.yaml`
- **Model Configuration Manager**: `src/core/model_config.py` for dynamic model loading
- **Model Manager CLI**: `src/utils/model_manager_cli.py` for command-line model management
- Comprehensive model documentation in `docs/MODEL_CONFIGURATION.md`
- Model configuration examples in `examples/model_config_examples.py`
- Unit tests for model configuration system: `tests/test_model_config.py`
- Integration with Settings class for seamless model access
- Support for multiple AI models:
  - Groq: Kimi K2, Llama 3 (70B, 8B), Mixtral 8x7B
  - xAI: Grok Beta, Grok Vision Beta
  - Local: Regelbaserad fallback

### Changed
- Updated `src/core/config.py` to integrate ModelConfigManager
- Enhanced Settings class with `get_model_config_manager()` and `get_model_for_profile()` methods
- Improved project structure documentation in README.md
- Updated all provider implementations for consistency

### Fixed
- **LocalProvider**: Added proper error handling with try/except blocks
- **LocalProvider**: Fixed streaming implementation to handle stream parameter correctly
- **LocalProvider**: Added input validation for None/empty inputs
- **LocalProvider**: Improved token counting with estimation
- **GroqProvider**: Added retry with exponential backoff
- **GroqProvider**: Enhanced token estimation in streaming mode
- **XAIProvider**: Fixed fallback mechanism for non-streaming scenarios
- **All Providers**: Consistent input validation
- **All Providers**: Enhanced docstrings following Google style

### Security
- Removed sensitive API keys from repository history
- Created `.env.template` with safe placeholder values
- Added comprehensive `.gitignore` for Python, IDE, and sensitive files
- Documented security best practices in `CODING_GUIDELINES.md`

## [6.0.0] - 2025-11-05

### Added
- Initial release of IRIS v6.0 - Förenklad och Robust Intelligensrapportering
- Multi-provider AI system with automatic fallback (Groq → xAI → Lokal)
- Three intelligent profiles:
  - **Snabb** (< 2s): Fast responses with Groq Kimi K2
  - **Smart** (3-7s): Balanced analysis with xAI Grok
  - **Privat** (5-15s): Fully local processing
- Svenska datakällor integration:
  - SCB (Statistiska centralbyrån)
  - OMX Stockholm
  - NewsData.io (svenska nyheter)
  - SMHI (väderdata)
- FastAPI-based REST API
- GDPR-compliant architecture
- Circuit breaker pattern for robust error handling
- Retry with exponential backoff
- Redis caching for performance
- SQLite/PostgreSQL hybrid database support
- Docker and Docker Compose support
- Comprehensive testing suite with pytest
- Swedish NLP support
- Structured logging with svenska språk

### Core Components
- `src/main.py`: FastAPI application
- `src/core/config.py`: Configuration management
- `src/core/database.py`: Database abstraction
- `src/core/security.py`: Security and GDPR compliance
- `src/services/ai_analyzer.py`: Multi-provider AI analysis
- `src/services/profile_router.py`: Profile routing logic
- `src/services/data_collector.py`: Data collection with circuit breakers
- `src/services/swedish_sources.py`: Swedish data source integration
- `src/services/ai_providers/`: Provider implementations
  - `base.py`: Abstract base provider
  - `groq_provider.py`: Groq Cloud integration
  - `xai_provider.py`: xAI Grok integration
  - `local_provider.py`: Local fallback provider
  - `factory.py`: Provider factory pattern

### Documentation
- Comprehensive README.md with svenska språk
- API documentation via FastAPI
- Testing guide in `TESTING.md`
- Coding guidelines in `CODING_GUIDELINES.md`
- Architecture diagrams and examples

### Testing
- Unit tests for all core components
- Integration tests for multi-provider fallback
- API endpoint tests
- Mock data for external services
- Coverage reporting with pytest-cov

## Types of Changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

## Versioning

IRIS follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

---

**Maintained by:** IRIS Development Team
**Project:** IRIS v6.0 - Intelligent Rapporteringssystem för Sverige 🇸🇪
