# 📚 IRIS v6.0 - Coding Guidelines

**Version:** 1.0 | **Projekt:** IRIS v6.0 - Intelligent Rapporteringssystem för Sverige

Dessa riktlinjer säkerställer enhetlig kodstandard oavsett om koden skrivs av utvecklare eller AI-agenter (Windsurf Cascade).

---

## 🐍 Python Standard

### Versioner
- **Python:** 3.10+ (Rekommenderad: 3.12)
- **Style:** PEP 8
- **Indentation:** 4 spaces
- **Line length:** Max 100 tecken
- **Encoding:** UTF-8

### Import Order
```python
# 1. Standard library
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# 2. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local
from src.core.config import Settings
from src.services.ai_providers.base import BaseAIProvider
```

---

## 🏷️ Naming Conventions

```python
# Variables & Functions: snake_case
user_query = "test"
def calculate_score() -> float:
    pass

# Classes: PascalCase
class AIAnalyzer:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Boolean: is_, has_, can_
is_authenticated = True
has_permission = False

# Private: Prefix _
def _internal_function():
    pass
```

---

## 🔤 Type Hints (Obligatoriska)

```python
# ✅ RÄTT
def analyze(
    query: str,
    context: Dict[str, Any],
    temperature: float = 0.7
) -> Dict[str, Any]:
    """Analysera query."""
    return {"result": "success"}

async def fetch_data(url: str) -> Optional[Dict[str, Any]]:
    """Hämta data."""
    return {"data": "value"}

# ❌ FEL - Inga type hints
def analyze(query, context):
    return {}
```

---

## ⚠️ Error Handling

```python
# ✅ RÄTT - Specifika exceptions med logging
try:
    result = await provider.analyze(query, context)
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise HTTPException(status_code=503, detail="Unavailable")
except Exception as e:
    logger.error(f"Unexpected: {e}", exc_info=True)
    raise

# Custom exceptions
class ProviderUnavailableException(Exception):
    """Provider inte tillgänglig."""
    pass

# Graceful fallback
for provider_name in ["groq", "xai", "lokal"]:
    try:
        return await get_provider(provider_name).analyze(query)
    except Exception:
        continue
```

---

## ⚡ Async/Await Patterns

```python
# ✅ RÄTT - Konsekvent async
async def fetch_data(url: str) -> Dict[str, Any]:
    """Hämta data asynkront."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Concurrent operations
async def process_multiple(urls: List[str]) -> List[Dict]:
    """Process flera URLs samtidigt."""
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

# Streaming
async def stream_response(provider) -> AsyncIterator[str]:
    """Stream svar."""
    async for chunk in provider.analyze_stream(query):
        if chunk:
            yield chunk

# ❌ FEL - Blocking i async
async def read_file(path):
    with open(path) as f:  # Blocking!
        return f.read()
```

---

## 📝 Logging

```python
import logging
logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debugging")     # Development
logger.info("✅ Normal operation")     # Production
logger.warning("⚠️ Warning message")   # Warnings  
logger.error("❌ Error occurred")      # Errors
logger.critical("🔥 Critical issue")   # Critical

# Structured logging med context
logger.info(
    "AI analysis completed",
    extra={
        "provider": "groq",
        "tokens": 1234,
        "duration": 1.5
    }
)

# Maskera sensitive data
masked_key = f"{api_key[:4]}...{api_key[-4:]}"
logger.info(f"Using key: {masked_key}")

# ❌ FEL
print("Debug info")  # Använd inte print
logger.info(f"API key: {full_api_key}")  # Logga inte keys!
```

---

## 🧪 Testing

```python
# Test structure
# tests/test_groq_provider.py

import pytest

class TestGroqProvider:
    """Test Groq provider."""
    
    def test_initialization(self):
        """Test provider init."""
        provider = GroqProvider(api_key="test")
        assert provider.get_provider_name() == "groq"
    
    @pytest.mark.asyncio
    async def test_analyze(self):
        """Test basic analysis."""
        provider = GroqProvider(api_key="test")
        # Test logic
    
    @pytest.mark.skipif(
        not os.getenv("GROQ_API_KEY"),
        reason="GROQ_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_real_api(self):
        """Test med real API."""
        provider = GroqProvider(api_key=os.getenv("GROQ_API_KEY"))
        result = await provider.analyze("Test", "")
        assert "svar" in result

# Minimum coverage: 85%
# pytest tests/ --cov=src --cov-report=html
```

---

## 📖 Documentation (Google Style)

```python
def analyze(
    query: str,
    context: Dict[str, Any],
    profile: str = "snabb"
) -> Dict[str, Any]:
    """
    Analysera användarfråga med AI.
    
    Använder multi-provider med fallback: Groq → xAI → Lokal.
    
    Args:
        query: Användarens fråga på svenska
        context: Kontextdata från källor (OMX, SCB, etc.)
        profile: AI-profil (snabb, smart, privat)
    
    Returns:
        Dict med struktur:
            - svar (str): AI-genererat svar
            - modell (str): Använd modell
            - provider (str): Använd provider
            - tokens_used (int): Tokens förbrukade
    
    Raises:
        ValueError: Om query är tom
        ProviderUnavailableException: Om alla providers misslyckas
    
    Example:
        >>> result = await analyze("Hur är vädret?", {})
        >>> print(result["svar"])
    """
    pass
```

---

## 🤖 AI Provider Implementation

```python
# Alla providers ska implementera BaseAIProvider
class BaseAIProvider(ABC):
    """Abstract base för providers."""
    
    @abstractmethod
    async def analyze(
        self,
        query: str,
        context: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Analysera (non-streaming)."""
        pass
    
    @abstractmethod
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """Analysera (streaming)."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider namn."""
        pass

# Provider implementation
class GroqProvider(BaseAIProvider):
    """Groq Cloud provider."""
    
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.client = AsyncGroq(api_key=api_key)
        logger.info("🚀 GroqProvider initialized")
    
    def get_provider_name(self) -> str:
        return "groq"
    
    async def analyze(self, ...) -> Dict[str, Any]:
        """Implement analysis."""
        try:
            # Null-safety checks
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            # API call med error handling
            completion = await self.client.chat.completions.create(...)
            
            # Safe response parsing
            content = completion.choices[0].message.content
            tokens = (
                completion.usage.total_tokens 
                if hasattr(completion, 'usage') 
                and completion.usage 
                and hasattr(completion.usage, 'total_tokens')
                else 0
            )
            
            return {
                "svar": content,
                "modell": model,
                "provider": "groq",
                "tokens_used": tokens
            }
        except Exception as e:
            logger.error(f"Groq error: {e}", exc_info=True)
            raise
```

---

## 🔒 Security

```python
# API Keys - Använd environment variables
from src.core.config import get_settings
settings = get_settings()
api_key = settings.groq_api_key

# ❌ NEVER hardcode keys
api_key = "gsk_1234..."  # NEVER!

# Input validation
from pydantic import BaseModel, validator

class Request(BaseModel):
    query: str
    
    @validator("query")
    def validate_query(cls, v):
        if not v or v.isspace():
            raise ValueError("Empty query")
        return v.strip()

# GDPR - No personal data in logs
logger.info("Analysis completed")  # ✅
logger.info(f"User email@example.com")  # ❌
```

---

## 🔀 Git Workflow

### Branch Naming
```bash
feature/groq-integration
bugfix/token-counting
hotfix/api-timeout
docs/update-readme
test/add-tests
```

### Commit Messages
```bash
# Format: type: description
feat: Add Groq Cloud provider with streaming
fix: Fix token counting AttributeError
docs: Update README with Groq setup
test: Add comprehensive provider tests
refactor: Improve error handling in analyzer
```

---

## 🌊 Windsurf/Cascade Best Practices

### För AI-Agenter (Windsurf Cascade)

#### 1. Alltid läs dessa guidelines först
```bash
# När du börjar arbeta:
@CODING_GUIDELINES.md
```

#### 2. Använd code_search för att förstå kodbasen
```python
# Innan du ändrar kod, använd:
code_search("Leta efter provider implementation")
code_search("Hur fungerar fallback-mekanismen")
```

#### 3. Verifiera ändringar
```python
# Efter varje ändring:
python -m py_compile file.py  # Syntax check
pytest tests/test_file.py -v  # Unit tests
```

#### 4. Följ projektets patterns
- **Provider pattern**: Alla AI providers ärver BaseAIProvider
- **Factory pattern**: Använd AIProviderFactory för att skapa providers
- **Async konsekvent**: Alla I/O är async
- **Error handling**: Try/except med logging och fallback

#### 5. Dokumentera ändringar
```python
# Innan commit, uppdatera:
# - CHANGELOG.md
# - Relevanta docstrings
# - Test coverage

# Skapa bugfix-rapport om buggar fixas
# - BUGFIXES_REPORT.md
```

#### 6. Test före commit
```bash
# Minimum checks:
pytest tests/ -v
python -m py_compile src/**/*.py
mypy src/ --ignore-missing-imports
```

---

## ✅ Code Review Checklist

Innan commit, verifiera:

- [ ] Type hints på alla funktioner
- [ ] Docstrings på publika funktioner/klasser
- [ ] Error handling med try/except
- [ ] Logging på rätt nivå
- [ ] Inga hardcoded secrets
- [ ] Async/await korrekt använt
- [ ] Tests skrivna/uppdaterade
- [ ] Syntax check passerar
- [ ] Import order korrekt
- [ ] GDPR-compliant (ingen PII i logs)

---

## 📚 Resurser

- **PEP 8**: https://pep8.org
- **Type Hints**: https://docs.python.org/3/library/typing.html
- **AsyncIO**: https://docs.python.org/3/library/asyncio.html
- **FastAPI**: https://fastapi.tiangolo.com
- **Pytest**: https://docs.pytest.org

---

## 🎯 Sammanfattning

**Viktigaste reglerna:**

1. **Type hints överallt**
2. **Async för all I/O**
3. **Error handling med logging**
4. **Test coverage > 85%**
5. **GDPR-compliant**
6. **Dokumentera public API**
7. **Följ naming conventions**
8. **Använd patterns (Factory, Provider)**

**För Windsurf Cascade:**
- Läs dessa guidelines innan arbete
- Använd code_search för att förstå context
- Verifiera syntax och tester
- Dokumentera alla ändringar

---

**✅ Följ dessa guidelines för enhetlig och produktionsklar kod!**
