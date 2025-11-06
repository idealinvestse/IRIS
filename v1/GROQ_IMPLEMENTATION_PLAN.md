# GROQ Cloud Implementation Plan - Kimi K2 Integration

## 📋 Översikt

Integrera Groq Cloud med Kimi K2-modellen som primär snabb AI-modell för IRIS v6.0.

**Mål:**
- ✅ Ersätt/komplettera xAI Grok med Groq Cloud
- ✅ Använd Kimi K2 (`moonshotai/kimi-k2-instruct-0905`) för snabb profil
- ✅ Behåll bakåtkompatibilitet med xAI
- ✅ Streaming-support för real-time svar
- ✅ Robust felhantering

## 🎯 Fas 1: Förberedelser och Dependencies

### 1.1 Installera Groq SDK

**Fil:** `requirements.txt`

```python
# Lägg till efter OpenAI
groq==0.11.0  # Groq Cloud SDK
```

### 1.2 Uppdatera Miljövariabler

**Fil:** `.env.example`

```bash
# =============================================================================
# AI OCH GROQ KONFIGURATION
# =============================================================================
# Groq Cloud API (primär för snabb profil)
GROQ_API_KEY=gsk_...
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_TIMEOUT=10

# xAI Grok API (fallback)
XAI_API_KEY=xai-...
XAI_BASE_URL=https://api.x.ai/v1
XAI_TIMEOUT=30
```

## 🎯 Fas 2: Konfigurationsuppdateringar

### 2.1 Uppdatera Settings

**Fil:** `src/core/config.py`

**Ändringar:**

```python
class Settings(BaseSettings):
    """Huvudkonfiguration för IRIS v6.0"""
    
    # ... befintliga fält ...
    
    # Groq Cloud (NYTT)
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", env="GROQ_BASE_URL")
    groq_timeout: int = Field(default=10, env="GROQ_TIMEOUT")
    groq_model_default: str = Field(default="moonshotai/kimi-k2-instruct-0905", env="GROQ_MODEL_DEFAULT")
    
    # xAI (behålls som fallback)
    xai_api_key: Optional[str] = Field(default=None, env="XAI_API_KEY")
    xai_base_url: str = Field(default="https://api.x.ai/v1", env="XAI_BASE_URL")
    xai_timeout: int = Field(default=30, env="XAI_TIMEOUT")
```

### 2.2 Uppdatera Profil-Konfiguration

**Fil:** `config/profiles.yaml`

**Ändringar:**

```yaml
profiles:
  snabb:
    beskrivning: "Snabba svar under 2 sekunder med Groq Kimi K2"
    ai_provider: "groq"  # NYTT: specificera provider
    ai_model: "moonshotai/kimi-k2-instruct-0905"
    max_källor: 2
    cache_ttl: 300
    förväntad_svarstid: "< 2 sekunder"
    externa_anrop: true
    timeout_seconds: 5
    streaming: true  # NYTT: stöd för streaming
    temperature: 0.6
    max_tokens: 4096
    
  smart:
    beskrivning: "Balanserad analys med xAI Grok"
    ai_provider: "xai"  # NYTT
    ai_model: "grok-beta"
    max_källor: 5
    cache_ttl: 600
    förväntad_svarstid: "3-7 sekunder"
    externa_anrop: true
    timeout_seconds: 15
    streaming: false
    temperature: 0.7
    max_tokens: 2048
  
  privat:
    beskrivning: "Helt lokal bearbetning"
    ai_provider: "lokal"  # NYTT
    ai_model: "lokal"
    max_källor: 3
    cache_ttl: 1800
    förväntad_svarstid: "5-15 sekunder"
    externa_anrop: false
    timeout_seconds: 30
    streaming: false
```

## 🎯 Fas 3: AI Analyzer Refaktorering

### 3.1 Skapa AI Provider Interface

**Ny fil:** `src/services/ai_providers/__init__.py`

```python
"""
AI Provider abstraktion för olika AI-tjänster
"""
```

### 3.2 Skapa Base Provider

**Ny fil:** `src/services/ai_providers/base.py`

```python
"""
Base AI Provider Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator

class BaseAIProvider(ABC):
    """Abstract base class för AI-providers"""
    
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
        """Analysera med AI"""
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
        """Streaming-analys"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Returnera provider-namn"""
        pass
```

### 3.3 Implementera Groq Provider

**Ny fil:** `src/services/ai_providers/groq_provider.py`

```python
"""
Groq Cloud Provider med Kimi K2
"""
import logging
from typing import Dict, Any, AsyncIterator
from groq import Groq, AsyncGroq
from .base import BaseAIProvider

logger = logging.getLogger(__name__)

class GroqProvider(BaseAIProvider):
    """Groq Cloud AI Provider"""
    
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.client = Groq(api_key=api_key)
        self.async_client = AsyncGroq(api_key=api_key)
        logger.info("🚀 GroqProvider initialiserad med Kimi K2")
    
    def get_provider_name(self) -> str:
        return "groq"
    
    async def analyze(
        self,
        query: str,
        context: str,
        model: str = "moonshotai/kimi-k2-instruct-0905",
        temperature: float = 0.6,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Analysera med Groq Kimi K2
        """
        try:
            prompt = self._build_prompt(query, context)
            
            if stream:
                # För streaming, samla allt innehåll
                full_content = ""
                async for chunk in self.analyze_stream(
                    query, context, model, temperature, max_tokens
                ):
                    full_content += chunk
                
                return {
                    "svar": full_content,
                    "modell": model,
                    "provider": "groq",
                    "typ": "ai_analysis_streaming",
                    "tokens_used": len(full_content.split())  # Approximation
                }
            else:
                # Non-streaming
                completion = await self.async_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Du är IRIS, en intelligent svensk assistent."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=False,
                    stop=None
                )
                
                content = completion.choices[0].message.content
                
                return {
                    "svar": content,
                    "modell": model,
                    "provider": "groq",
                    "typ": "ai_analysis",
                    "tokens_used": completion.usage.total_tokens if completion.usage else 0
                }
                
        except Exception as e:
            logger.error(f"Groq API fel: {e}")
            raise
    
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str = "moonshotai/kimi-k2-instruct-0905",
        temperature: float = 0.6,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """
        Streaming-analys med Groq
        """
        try:
            prompt = self._build_prompt(query, context)
            
            stream = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du är IRIS, en intelligent svensk assistent."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=True,
                stop=None
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Groq streaming fel: {e}")
            raise
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Bygg prompt på svenska"""
        return f"""Du är IRIS, en intelligent svensk assistent.

Användarfråga: {query}

Kontext från svenska datakällor:
{context}

Ge ett komplett, informativt svar på svenska baserat på kontexten ovan."""
```

### 3.4 Implementera xAI Provider

**Ny fil:** `src/services/ai_providers/xai_provider.py`

```python
"""
xAI Grok Provider (behålls som fallback)
"""
import logging
from typing import Dict, Any, AsyncIterator
import aiohttp
from .base import BaseAIProvider

logger = logging.getLogger(__name__)

class XAIProvider(BaseAIProvider):
    """xAI Grok Provider"""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        logger.info("🧠 XAIProvider initialiserad")
    
    def get_provider_name(self) -> str:
        return "xai"
    
    async def analyze(
        self,
        query: str,
        context: str,
        model: str = "grok-beta",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Analysera med xAI Grok"""
        # Befintlig implementation från ai_analyzer.py
        # ... (kopiera från nuvarande _analyze_with_xai)
        pass
    
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str = "grok-beta",
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> AsyncIterator[str]:
        """xAI stödjer inte streaming än"""
        raise NotImplementedError("xAI streaming är inte tillgängligt")
```

### 3.5 Lokal Provider

**Ny fil:** `src/services/ai_providers/local_provider.py`

```python
"""
Lokal AI Provider (regelbaserad)
"""
import logging
from typing import Dict, Any, AsyncIterator
from .base import BaseAIProvider

logger = logging.getLogger(__name__)

class LocalProvider(BaseAIProvider):
    """Lokal regelbaserad provider"""
    
    def get_provider_name(self) -> str:
        return "lokal"
    
    async def analyze(
        self,
        query: str,
        context: str,
        model: str = "lokal",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Enkel lokal analys"""
        # Befintlig implementation från ai_analyzer.py
        # ... (kopiera från nuvarande _analyze_locally)
        pass
    
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str = "lokal",
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """Lokal streaming"""
        result = await self.analyze(query, context, model, temperature, max_tokens)
        yield result["svar"]
```

### 3.6 Provider Factory

**Ny fil:** `src/services/ai_providers/factory.py`

```python
"""
AI Provider Factory
"""
import logging
from typing import Optional
from .base import BaseAIProvider
from .groq_provider import GroqProvider
from .xai_provider import XAIProvider
from .local_provider import LocalProvider

logger = logging.getLogger(__name__)

class AIProviderFactory:
    """Factory för att skapa AI-providers"""
    
    @staticmethod
    def create_provider(
        provider_name: str,
        settings
    ) -> Optional[BaseAIProvider]:
        """
        Skapa AI-provider baserat på namn
        """
        provider_name = provider_name.lower()
        
        if provider_name == "groq":
            if not settings.groq_api_key:
                logger.warning("Groq API-nyckel saknas")
                return None
            return GroqProvider(
                api_key=settings.groq_api_key,
                timeout=settings.groq_timeout
            )
        
        elif provider_name == "xai":
            if not settings.xai_api_key:
                logger.warning("xAI API-nyckel saknas")
                return None
            return XAIProvider(
                api_key=settings.xai_api_key,
                base_url=settings.xai_base_url,
                timeout=settings.xai_timeout
            )
        
        elif provider_name == "lokal":
            return LocalProvider()
        
        else:
            logger.error(f"Okänd provider: {provider_name}")
            return None
```

### 3.7 Uppdatera AI Analyzer

**Fil:** `src/services/ai_analyzer.py`

**Stora ändringar:**

```python
"""
IRIS v6.0 - AI Analyzer (Uppdaterad)
Multi-provider support med Groq, xAI och lokal
"""
import logging
from typing import Dict, Any
from src.services.ai_providers.factory import AIProviderFactory

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    AI-analys med multi-provider support
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        self.provider_cache = {}
        logger.info("🧠 AIAnalyzer initialiserad (multi-provider)")
    
    async def analyze(
        self,
        query: str,
        context_data: Dict[str, Any],
        profile: str,
        profile_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analysera fråga med vald AI-provider
        """
        # Hämta provider från profil
        provider_name = profile_config.get("ai_provider", "lokal")
        model = profile_config.get("ai_model", "lokal")
        temperature = profile_config.get("temperature", 0.7)
        max_tokens = profile_config.get("max_tokens", 2048)
        streaming = profile_config.get("streaming", False)
        
        logger.info(f"🤖 Analyserar med provider: {provider_name}, modell: {model}")
        
        # Hämta eller skapa provider
        provider = self._get_provider(provider_name)
        
        if not provider:
            logger.warning(f"Provider {provider_name} inte tillgänglig, använder lokal")
            provider = self._get_provider("lokal")
        
        # Bygg kontext
        context = self._build_context(context_data)
        
        try:
            # Analysera
            result = await provider.analyze(
                query=query,
                context=context,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=streaming
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Provider {provider_name} misslyckades: {e}")
            
            # Försök fallback till xAI, sedan lokal
            for fallback_name in ["xai", "lokal"]:
                if fallback_name != provider_name:
                    try:
                        logger.info(f"Försöker fallback: {fallback_name}")
                        fallback_provider = self._get_provider(fallback_name)
                        if fallback_provider:
                            return await fallback_provider.analyze(
                                query, context, model="lokal", 
                                temperature=0.5, max_tokens=1000
                            )
                    except Exception as fallback_error:
                        logger.error(f"Fallback {fallback_name} misslyckades: {fallback_error}")
            
            # Om allt misslyckas, returnera fel-meddelande
            return self._error_response(query, e)
    
    def _get_provider(self, provider_name: str):
        """Hämta eller skapa provider (cached)"""
        if provider_name not in self.provider_cache:
            self.provider_cache[provider_name] = AIProviderFactory.create_provider(
                provider_name, self.settings
            )
        return self.provider_cache[provider_name]
    
    def _build_context(self, context_data: Dict[str, Any]) -> str:
        """Bygg kontext från data"""
        # Befintlig implementation
        pass
    
    def _error_response(self, query: str, error: Exception) -> Dict[str, Any]:
        """Fel-respons"""
        return {
            "svar": f"Kunde inte analysera frågan '{query}' på grund av tekniska problem.",
            "modell": "error",
            "provider": "none",
            "typ": "error",
            "tokens_used": 0,
            "error": str(error)
        }
```

## 🎯 Fas 4: Testing

### 4.1 Groq Provider Tests

**Ny fil:** `tests/test_groq_provider.py`

```python
"""
IRIS v6.0 - Groq Provider Tests
"""
import pytest
from src.services.ai_providers.groq_provider import GroqProvider

@pytest.mark.asyncio
class TestGroqProvider:
    """Test Groq Cloud provider"""
    
    async def test_provider_initialization(self):
        """Test Groq provider initialisering"""
        provider = GroqProvider(api_key="test-key")
        assert provider.get_provider_name() == "groq"
    
    @pytest.mark.skipif(
        not os.getenv("GROQ_API_KEY"),
        reason="GROQ_API_KEY not set"
    )
    async def test_analyze_with_real_api(self):
        """Test analys med riktig API"""
        provider = GroqProvider(api_key=os.getenv("GROQ_API_KEY"))
        
        result = await provider.analyze(
            query="Vad är 2+2?",
            context="",
            model="moonshotai/kimi-k2-instruct-0905"
        )
        
        assert "svar" in result
        assert result["provider"] == "groq"
    
    async def test_streaming(self):
        """Test streaming-funktionalitet"""
        # Mock test för streaming
        pass
```

### 4.2 AI Analyzer Tests

**Uppdatera:** `tests/test_ai_analyzer.py`

```python
@pytest.mark.asyncio
async def test_groq_provider_selection():
    """Test att Groq väljs för snabb profil"""
    analyzer = AIAnalyzer()
    
    profile_config = {
        "ai_provider": "groq",
        "ai_model": "moonshotai/kimi-k2-instruct-0905",
        "temperature": 0.6,
        "max_tokens": 4096
    }
    
    # Mock analyze
    # ...
```

## 🎯 Fas 5: Dokumentation

### 5.1 Uppdatera README

**Fil:** `README.md`

Lägg till sektion om Groq:

```markdown
### AI-Providers

IRIS v6.0 stödjer flera AI-providers:

1. **Groq Cloud** (Standard för snabb profil)
   - Modell: Kimi K2 (`moonshotai/kimi-k2-instruct-0905`)
   - Snabb responstid (< 2s)
   - Streaming-support
   
2. **xAI Grok** (Smart profil)
   - Modell: grok-beta
   - Djup analys

3. **Lokal** (Privat profil)
   - Regelbaserad
   - Ingen extern kommunikation
```

### 5.2 API-dokumentation

Uppdatera FastAPI docs med streaming-exempel.

## 🎯 Fas 6: Implementation Checklist

### Steg-för-steg

- [ ] **Fas 1: Dependencies**
  - [ ] Installera groq SDK
  - [ ] Uppdatera requirements.txt
  - [ ] Uppdatera .env.example

- [ ] **Fas 2: Konfiguration**
  - [ ] Uppdatera Settings i config.py
  - [ ] Uppdatera profiles.yaml
  - [ ] Lägg till groq-specifika inställningar

- [ ] **Fas 3: Provider Implementation**
  - [ ] Skapa ai_providers/ directory
  - [ ] Implementera base.py
  - [ ] Implementera groq_provider.py
  - [ ] Implementera xai_provider.py
  - [ ] Implementera local_provider.py
  - [ ] Implementera factory.py
  - [ ] Refaktorera ai_analyzer.py

- [ ] **Fas 4: Testing**
  - [ ] Skapa test_groq_provider.py
  - [ ] Uppdatera test_ai_analyzer.py
  - [ ] Kör alla tester
  - [ ] Verifiera streaming

- [ ] **Fas 5: Dokumentation**
  - [ ] Uppdatera README.md
  - [ ] Uppdatera API-dokumentation
  - [ ] Skapa GROQ_GUIDE.md

- [ ] **Fas 6: Deployment**
  - [ ] Testa i utvecklingsmiljö
  - [ ] Uppdatera Docker-konfiguration
  - [ ] Production deployment

## 📊 Förväntade Resultat

### Prestanda

- **Snabb profil (Groq Kimi K2)**: < 2s responstid
- **Smart profil (xAI Grok)**: 3-7s responstid
- **Privat profil (Lokal)**: 5-15s responstid

### Fördelar

✅ Mycket snabbare responstider med Groq
✅ Streaming-support för real-time upplevelse
✅ Cost-effective (Groq ofta billigare)
✅ Fallback till xAI/lokal vid problem
✅ Modulär arkitektur - lätt lägga till nya providers

## 🚨 Risker och Mitigation

| Risk | Sannolikhet | Impact | Mitigation |
|------|-------------|--------|------------|
| Groq API downtime | Medel | Hög | Automatisk fallback till xAI |
| API-kostnader | Låg | Medel | Rate limiting, caching |
| Breaking changes i Groq SDK | Låg | Medel | Pin version i requirements.txt |
| Streaming-problem | Medel | Låg | Non-streaming fallback |

## 📅 Tidsestimat

- **Fas 1-2 (Dependencies & Config)**: 30 min
- **Fas 3 (Implementation)**: 2-3 timmar
- **Fas 4 (Testing)**: 1-2 timmar
- **Fas 5 (Documentation)**: 30 min
- **Fas 6 (Deployment & Validation)**: 1 timme

**Total**: 5-7 timmar

## ✅ Definition of Done

- [ ] Groq provider fungerar med Kimi K2
- [ ] Streaming fungerar korrekt
- [ ] Alla tester går igenom (inkl. nya Groq-tester)
- [ ] Fallback till xAI fungerar
- [ ] Dokumentation uppdaterad
- [ ] Performance-mål uppnådda (< 2s för snabb profil)
- [ ] Deployed och verifierad i test-miljö
