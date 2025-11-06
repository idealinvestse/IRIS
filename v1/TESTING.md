# IRIS v6.0 - Testing Guide

## 📋 Översikt

IRIS v6.0 har omfattande enhetstester som täcker alla huvudkomponenter:

- **Core Modules**: Konfiguration, databas, säkerhet
- **Services**: Profile routing, data collection, AI analysis, svenska källor
- **Utilities**: Error handling, circuit breakers, NLP
- **API**: FastAPI endpoints
- **Integration**: End-to-end tester

## 🚀 Kör Tester

### Installera Test-Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Kör Alla Tester

```bash
# Enkel körning
pytest

# Med verbose output
pytest -v

# Med coverage-rapport
pytest --cov=src --cov-report=html --cov-report=term

# Endast unit tests
pytest tests/ -m unit

# Endast integration tests
pytest tests/ -m integration
```

### Kör Specifika Test-Filer

```bash
# Config tests
pytest tests/test_config.py -v

# Database tests
pytest tests/test_database.py -v

# Security tests
pytest tests/test_security.py -v

# Error handling tests
pytest tests/test_error_handling.py -v

# NLP tests
pytest tests/test_nlp.py -v

# Swedish sources tests
pytest tests/test_swedish_sources.py -v

# API tests
pytest tests/test_api.py -v

# Integration tests
pytest tests/test_integration.py -v
```

### Kör Specifika Test-Funktioner

```bash
# En specifik test
pytest tests/test_config.py::TestConfiguration::test_default_profiles -v

# Alla tester i en klass
pytest tests/test_security.py::TestSecurity -v
```

## 📊 Test Coverage

För att generera coverage-rapport:

```bash
# HTML-rapport
pytest --cov=src --cov-report=html
# Öppna sedan htmlcov/index.html i webbläsare

# Terminal-rapport
pytest --cov=src --cov-report=term-missing

# XML-rapport (för CI/CD)
pytest --cov=src --cov-report=xml
```

## 🔧 Test-Konfiguration

Test-konfigurationen finns i `pytest.ini` och `tests/conftest.py`.

### Miljövariabler för Tester

Tester använder följande miljövariabler (automatiskt satta):

```bash
ENVIRONMENT=test
DEBUG=true
DATABASE_URL=sqlite:///:memory:
GDPR_ENABLED=true
XAI_API_KEY=test-key-12345
```

## 📝 Skriva Nya Tester

### Test-Struktur

```python
import pytest

class TestDinKomponent:
    """Beskrivning av test-suite"""
    
    def test_grundläggande_funktionalitet(self):
        """Test beskrivning"""
        # Arrange
        ...
        
        # Act
        ...
        
        # Assert
        assert ...
```

### Async Tester

```python
@pytest.mark.asyncio
class TestAsyncKomponent:
    async def test_async_funktion(self):
        """Test async funktionalitet"""
        result = await async_function()
        assert result is not None
```

### Fixtures

Använd fixtures från `conftest.py`:

```python
def test_med_settings(test_settings):
    """Test med settings fixture"""
    assert test_settings.environment == "test"

async def test_med_databas(test_db):
    """Test med databas fixture"""
    is_healthy = await test_db.health_check()
    assert is_healthy
```

## 🎯 Test-Kategorier

### Unit Tests

Tester som testar en enskild komponent isolerat:

```bash
pytest tests/test_config.py tests/test_security.py tests/test_nlp.py
```

### Integration Tests

Tester som testar integration mellan komponenter:

```bash
pytest tests/test_integration.py -v
```

### API Tests

Tester som testar HTTP endpoints:

```bash
pytest tests/test_api.py -v
```

## 🐛 Debugging Tester

### Kör med Debugging

```bash
# Med Python debugger
pytest --pdb

# Stoppa vid första felet
pytest -x

# Visa lokala variabler vid fel
pytest -l

# Verbose output
pytest -vv
```

### Kör Endast Misslyckade Tester

```bash
# Första gången
pytest

# Kör endast misslyckade
pytest --lf

# Kör misslyckade först, sedan resten
pytest --ff
```

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## ✅ Best Practices

1. **Skriv tester först** (TDD när möjligt)
2. **Ett assert per test** (helst)
3. **Tydliga test-namn** som beskriver vad som testas
4. **Använd fixtures** för återanvändbar setup
5. **Mock externa beroenden** när lämpligt
6. **Testa edge cases** och fel-scenarier
7. **Håll tester snabba** - isolera långsamma tester
8. **Uppdatera tester** när kod ändras

## 🎪 Mock Data

Tester använder mock data för externa API:er:

- **OMX**: Simulerad börsdata
- **SCB**: Simulerad statistik
- **SMHI**: Simulerad väderdata
- **News**: Simulerade nyheter

Detta gör testerna:
- ✅ Snabbare
- ✅ Pålitligare (ingen nätverks-dependency)
- ✅ Reproducerbara
- ✅ Körbara offline

## 📚 Ytterligare Resurser

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
