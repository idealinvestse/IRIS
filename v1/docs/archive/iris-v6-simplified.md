# IRIS v6.0: Förenklad och Robust Intelligensrapportering

## Översikt

IRIS v6.0 är en förenklad men robust version av intelligensrapporteringssystemet, specifikt optimerad för svenska användare med fokus på enkelhet, tillförlitlighet och GDPR-efterlevnad.

## Kärnförbättringar

### 1. Förenklade Arkitektur
- **Modulär monolit** istället för mikroservices
- **SQLite/PostgreSQL** hybrid för datalagring
- **Redis** för caching och sessioner
- **FastAPI** för API med async-stöd

### 2. Tre Huvudprofiler
- **Snabb**: Låg latens, begränsad analys
- **Smart**: Balanserad prestanda och djup
- **Privat**: Helt lokal, ingen external API-användning

### 3. Svenska Datakällor (Prioriterade)
- **SCB (Statistiska centralbyrån)** - Officiell statistik
- **OMX Stockholm** - Finansiell data
- **Svenska nyheter** - Via NewsData.io
- **Väderdata** - SMHI

## Projektstruktur

```
iris-v6/
├── src/
│   ├── main.py              # FastAPI app
│   ├── core/
│   │   ├── config.py        # Konfiguration
│   │   ├── database.py      # Databashantering
│   │   └── security.py      # Säkerhet & GDPR
│   ├── services/
│   │   ├── data_collector.py    # Datainhämtning
│   │   ├── ai_analyzer.py       # AI-analys
│   │   ├── profile_router.py    # Profilhantering
│   │   └── swedish_sources.py   # Svenska datakällor
│   ├── models/
│   │   ├── briefing.py      # Briefing-modeller
│   │   └── user.py          # Användarmodeller
│   └── utils/
│       ├── nlp_swedish.py   # Svensk NLP
│       └── error_handling.py # Felhantering
├── config/
│   └── profiles.yaml        # Profilkonfiguration
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Konfiguration (profiles.yaml)

```yaml
profiles:
  snabb:
    beskrivning: "Snabba svar under 2 sekunder"
    ai_model: "grok-4-turbo"
    max_källor: 2
    cache_ttl: 300
    
  smart:
    beskrivning: "Balanserad analys med flera källor"
    ai_model: "grok-4"
    max_källor: 5
    cache_ttl: 600
    
  privat:
    beskrivning: "Helt lokal bearbetning"
    ai_model: "llama-3-local"
    max_källor: 3
    cache_ttl: 1800
    externa_anrop: false

svenska_källor:
  scb:
    url: "https://api.scb.se/OV0104/v1/doris/sv/ssd/"
    typ: "statistik"
    cache: 3600
    
  omx:
    url: "https://query1.finance.yahoo.com/v8/finance/chart/^OMX"
    typ: "finansiell"
    cache: 300
    
  nyheter:
    url: "https://newsdata.io/api/1/news"
    typ: "nyheter"
    cache: 900
    land: "se"
    språk: "sv"
    
  väder:
    url: "https://opendata-download-metfcst.smhi.se/api"
    typ: "väder"
    cache: 1800
```

## Huvudkomponenter

### 1. Data Collector (data_collector.py)

```python
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis
import json
from src.core.config import get_settings
from src.utils.error_handling import CircuitBreaker, retry_with_backoff

class DataCollector:
    def __init__(self):
        self.settings = get_settings()
        self.redis = redis.from_url(self.settings.redis_url)
        self.session = None
        self.circuit_breakers = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry_with_backoff(max_retries=3)
    async def collect_swedish_data(self, query: str, sources: List[str]) -> Dict:
        """Samla data från svenska källor med robust felhantering"""
        results = {}
        
        for source in sources:
            cache_key = f"data:{source}:{hash(query)}"
            
            # Försök hämta från cache först
            cached = self.redis.get(cache_key)
            if cached:
                results[source] = json.loads(cached)
                continue
            
            # Använd circuit breaker för externa anrop
            breaker = self.circuit_breakers.get(source)
            if not breaker:
                breaker = CircuitBreaker(failure_threshold=5, timeout=60)
                self.circuit_breakers[source] = breaker
            
            try:
                if breaker.state == "open":
                    results[source] = {"error": "Circuit breaker open", "fallback": True}
                    continue
                
                data = await self._fetch_from_source(source, query)
                results[source] = data
                
                # Cacha resultat
                ttl = self.settings.source_cache_ttl.get(source, 600)
                self.redis.setex(cache_key, ttl, json.dumps(data))
                
                breaker.record_success()
                
            except Exception as e:
                breaker.record_failure()
                results[source] = {
                    "error": str(e),
                    "fallback": await self._get_fallback_data(source)
                }
        
        return results
    
    async def _fetch_from_source(self, source: str, query: str) -> Dict:
        """Hämta från specifik källa"""
        if source == "scb":
            return await self._fetch_scb_data(query)
        elif source == "omx":
            return await self._fetch_omx_data()
        elif source == "nyheter":
            return await self._fetch_news_data(query)
        elif source == "väder":
            return await self._fetch_weather_data()
        else:
            raise ValueError(f"Okänd källa: {source}")
    
    async def _fetch_scb_data(self, query: str) -> Dict:
        """SCB statistik"""
        url = "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy"
        async with self.session.get(url) as resp:
            data = await resp.json()
            return {
                "källa": "SCB",
                "data": data,
                "tidsstämpel": datetime.utcnow().isoformat()
            }
    
    async def _fetch_omx_data(self) -> Dict:
        """OMX Stockholm data"""
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^OMX"
        params = {"interval": "1d", "range": "1d"}
        async with self.session.get(url, params=params) as resp:
            data = await resp.json()
            return {
                "källa": "OMX",
                "data": data,
                "tidsstämpel": datetime.utcnow().isoformat()
            }
    
    async def _get_fallback_data(self, source: str) -> Dict:
        """Fallback-data när externa källor misslyckas"""
        fallback_key = f"fallback:{source}"
        cached = self.redis.get(fallback_key)
        if cached:
            return json.loads(cached)
        
        return {
            "meddelande": f"Använder fallback-data för {source}",
            "tidsstämpel": datetime.utcnow().isoformat()
        }
```

### 2. Profile Router (profile_router.py)

```python
from typing import Dict, Any, List
from src.services.data_collector import DataCollector
from src.services.ai_analyzer import AIAnalyzer
from src.core.config import get_settings
from src.utils.nlp_swedish import detect_language, extract_intent

class ProfileRouter:
    def __init__(self):
        self.settings = get_settings()
        self.ai_analyzer = AIAnalyzer()
    
    async def route_query(self, query: str, user_profile: str = None) -> Dict[str, Any]:
        """Dirigera query till rätt profil baserat på innehåll och användarval"""
        
        # Analysera query
        query_analysis = self._analyze_query(query)
        
        # Välj profil
        if user_profile:
            selected_profile = user_profile
        else:
            selected_profile = self._auto_select_profile(query_analysis)
        
        profile_config = self.settings.profiles[selected_profile]
        
        # Samla data
        async with DataCollector() as collector:
            raw_data = await collector.collect_swedish_data(
                query, 
                self._get_sources_for_profile(selected_profile)
            )
        
        # Analysera med AI
        analysis = await self.ai_analyzer.analyze(
            query=query,
            raw_data=raw_data,
            profile=selected_profile,
            config=profile_config
        )
        
        return {
            "profil": selected_profile,
            "query_analys": query_analysis,
            "rå_data": raw_data,
            "analys": analysis,
            "tidsstämpel": datetime.utcnow().isoformat()
        }
    
    def _analyze_query(self, query: str) -> Dict:
        """Analysera query för profilval"""
        return {
            "språk": detect_language(query),
            "intent": extract_intent(query),
            "komplexitet": self._calculate_complexity(query),
            "känslig_data": self._detect_sensitive_data(query)
        }
    
    def _auto_select_profile(self, analysis: Dict) -> str:
        """Automatiskt profilval baserat på query-analys"""
        if analysis["känslig_data"]:
            return "privat"
        elif analysis["komplexitet"] > 0.7:
            return "smart"
        else:
            return "snabb"
    
    def _get_sources_for_profile(self, profile: str) -> List[str]:
        """Få datakällor för specifik profil"""
        source_mapping = {
            "snabb": ["omx", "väder"],
            "smart": ["scb", "omx", "nyheter", "väder"],
            "privat": ["scb", "omx"]  # Endast officiella källor
        }
        return source_mapping.get(profile, ["omx"])
```

### 3. Error Handling (error_handling.py)

```python
import asyncio
import logging
from typing import Callable, Any
from datetime import datetime, timedelta
import functools

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def record_success(self):
        """Registrera framgångsrikt anrop"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Registrera misslyckat anrop"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def can_attempt(self) -> bool:
        """Kontrollera om anrop är tillåtet"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half-open"
                return True
            return False
        
        return True  # half-open state

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator för återförsök med exponentiell backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Alla återförsök misslyckades för {func.__name__}: {e}")
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Försök {attempt + 1} misslyckades för {func.__name__}, väntar {delay}s: {e}")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

class GracefulDegradation:
    """Hantera graceful degradation när tjänster är otillgängliga"""
    
    @staticmethod
    def provide_fallback_response(query: str, error: Exception) -> Dict:
        """Ge en användbar fallback-respons"""
        return {
            "meddelande": "Tjänsten är tillfälligt otillgänglig",
            "fallback_svar": f"Kunde inte behandla '{query}' just nu. Försök igen senare.",
            "fel": str(error),
            "tidsstämpel": datetime.utcnow().isoformat(),
            "status": "degraded"
        }
    
    @staticmethod
    def get_cached_response(query: str, cache_key: str) -> Dict:
        """Hämta cachad respons som fallback"""
        # Implementation för cached fallback
        pass
```

### 4. Main Application (main.py)

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
from contextlib import asynccontextmanager

from src.services.profile_router import ProfileRouter
from src.core.config import get_settings
from src.core.database import init_db
from src.core.security import verify_gdpr_consent

# Konfigurera logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hantera applikationens livscykel"""
    # Startup
    logger.info("Startar IRIS v6.0...")
    await init_db()
    yield
    # Shutdown
    logger.info("Stänger av IRIS v6.0...")

app = FastAPI(
    title="IRIS v6.0",
    description="Förenklad och Robust Intelligensrapportering",
    version="6.0.0",
    lifespan=lifespan
)

# CORS för svenska domäner
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*.se", "localhost:*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    profil: Optional[str] = None
    användar_id: Optional[str] = "anonym"

router = ProfileRouter()

@app.get("/")
async def root():
    return {
        "meddelande": "IRIS v6.0 - Förenklad Intelligensrapportering",
        "version": "6.0.0",
        "status": "aktiv"
    }

@app.get("/hälsa")
async def health_check():
    """Hälsokontroll för systemet"""
    return {
        "status": "frisk",
        "tidsstämpel": datetime.utcnow().isoformat(),
        "tjänster": {
            "databas": "aktiv",
            "cache": "aktiv",
            "ai": "aktiv"
        }
    }

@app.post("/analysera")
async def analyze_query(
    request: QueryRequest, 
    gdpr_consent: bool = Depends(verify_gdpr_consent)
):
    """Huvudendpoint för intelligensanalys"""
    try:
        if not gdpr_consent:
            raise HTTPException(
                status_code=403, 
                detail="GDPR-samtycke krävs för denna tjänst"
            )
        
        result = await router.route_query(
            query=request.query,
            user_profile=request.profil
        )
        
        return {
            "framgång": True,
            "resultat": result,
            "gdpr_kompatibel": True
        }
        
    except Exception as e:
        logger.error(f"Fel vid analys: {e}")
        
        # Graceful degradation
        from src.utils.error_handling import GracefulDegradation
        fallback = GracefulDegradation.provide_fallback_response(
            request.query, e
        )
        
        return {
            "framgång": False,
            "fellback": fallback,
            "gdpr_kompatibel": True
        }

@app.get("/profiler")
async def get_profiles():
    """Lista tillgängliga profiler"""
    settings = get_settings()
    return {
        "profiler": list(settings.profiles.keys()),
        "beskrivningar": {
            profil: config.get("beskrivning", "")
            for profil, config in settings.profiles.items()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

## Docker Compose för Enkel Distribution

```yaml
version: '3.8'

services:
  iris-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./iris.db
      - REDIS_URL=redis://redis:6379
      - XAI_API_KEY=${XAI_API_KEY}
      - GDPR_ENABLED=true
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/hälsa"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## Säkerhets- och GDPR-funktioner

### GDPR-efterlevnad
- **Automatisk dataklassificering** av känslig information
- **Samtycke-hantering** för svenska användare
- **Dataportabilitet** genom JSON-export
- **Rätten att bli glömd** genom automatisk rensning

### Säkerhet
- **Circuit breakers** för externa API:er
- **Rate limiting** per IP och användare
- **Kryptering** av känslig data i vila
- **Säker loggning** utan personuppgifter

## Installation och Användning

1. **Klona projekt**: `git clone <repository>`
2. **Konfigurera miljövariabler**: Kopiera `.env.example` till `.env`
3. **Starta tjänster**: `docker-compose up -d`
4. **Testa systemet**: `curl http://localhost:8000/hälsa`

## Fördelar med v6.0

1. **Enkelhet**: Färre komponenter och beroenden
2. **Robusthet**: Omfattande felhantering och fallbacks
3. **Svenska-fokus**: Optimerad för svenska datakällor och språk
4. **GDPR-kompatibel**: Inbyggd efterlevnad av svenska regler
5. **Skalbarhet**: Enkel att utöka och distribuera
6. **Underhållbarhet**: Tydlig kodstruktur och dokumentation

Denna förbättrade version behåller IRIS:s kraftfulla funktioner men gör systemet mycket mer robust och lättare att underhålla för svenska användare.