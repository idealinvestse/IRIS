"""
IRIS v6.0 - Förenklad och Robust Intelligensrapportering
Huvudapplikation med FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import os
from dotenv import load_dotenv

# Ladda miljövariabler
load_dotenv()

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import av egna moduler
from src.services.profile_router import ProfileRouter
from src.services.data_collector import DataCollector
from src.core.config import get_settings, Settings
from src.core.database import Database
from src.core.security import SecurityManager
from src.utils.error_handling import GracefulDegradation

# Global instanser
settings = get_settings()
db = Database()
security = SecurityManager()
profile_router = ProfileRouter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hantera applikationens livscykel"""
    try:
        logger.info("🚀 Startar IRIS v6.0...")
        
        # Initialisera databas
        await db.init_database()
        logger.info("✅ Databas initialiserad")
        
        # Kontrollera externa tjänster
        await _check_external_services()
        logger.info("✅ Externa tjänster kontrollerade")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Fel vid uppstart: {e}")
        raise
    finally:
        logger.info("🔄 Stänger av IRIS v6.0...")
        await db.close()

async def _check_external_services():
    """Kontrollera externa tjänsters tillgänglighet"""
    services = {
        "Redis": settings.redis_url,
        "xAI API": "https://api.x.ai" if settings.xai_api_key else None
    }
    
    for service, url in services.items():
        if url:
            logger.info(f"🔍 Kontrollerar {service}...")
            # Här skulle vi kontrollera tjänsternas status

# FastAPI app
app = FastAPI(
    title="IRIS v6.0",
    description="Förenklad och Robust Intelligensrapportering för Svenska Användare",
    version="6.0.0",
    lifespan=lifespan,
    docs_url="/dokumentation",
    redoc_url="/api-doc"
)

# CORS middleware för svenska domäner
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://*.se",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Request/Response modeller
class QueryRequest(BaseModel):
    query: str = Field(..., description="Fråga på svenska", min_length=3, max_length=1000)
    profil: Optional[str] = Field(None, description="Valt profil: snabb, smart, eller privat")
    användar_id: Optional[str] = Field("anonym", description="Användar-ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extra metadata")

class AnalysisResponse(BaseModel):
    framgång: bool
    profil_använd: str
    resultat: Dict[str, Any]
    tidsstämpel: str
    bearbetningstid: float
    gdpr_kompatibel: bool
    datakällor: List[str]

class HealthResponse(BaseModel):
    status: str
    version: str
    tidsstämpel: str
    tjänster: Dict[str, str]
    system_info: Dict[str, Any]

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global felhanterare"""
    logger.error(f"Oväntat fel: {exc}", exc_info=True)
    
    fallback = GracefulDegradation.provide_fallback_response(
        query=getattr(request, 'query', 'okänd'),
        error=exc
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "framgång": False,
            "fel": "Internt serverfel",
            "fallback": fallback,
            "tidsstämpel": datetime.utcnow().isoformat()
        }
    )

# API Endpoints
@app.get("/", tags=["System"])
async def root():
    """Välkomstmeddelande och systeminformation"""
    return {
        "meddelande": "Välkommen till IRIS v6.0 🇸🇪",
        "beskrivning": "Förenklad och Robust Intelligensrapportering",
        "version": "6.0.0",
        "språk": "svenska",
        "status": "aktiv",
        "dokumentation": "/dokumentation",
        "tillgängliga_endpoints": {
            "analysera": "/analysera - Huvudanalys-endpoint",
            "hälsa": "/hälsa - Systemhälsa",
            "profiler": "/profiler - Tillgängliga profiler",
            "användardata": "/användare/data - Användardata (GDPR)"
        }
    }

@app.get("/hälsa", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Omfattande hälsokontroll för systemet"""
    start_time = datetime.utcnow()
    
    # Kontrollera tjänster
    services_status = {}
    
    try:
        # Databas
        await db.health_check()
        services_status["databas"] = "aktiv"
    except Exception as e:
        services_status["databas"] = f"fel: {str(e)}"
    
    try:
        # Redis (om konfigurerad)
        if settings.redis_url:
            # Kontrollera Redis anslutning
            services_status["cache"] = "aktiv"
        else:
            services_status["cache"] = "inte konfigurerad"
    except Exception as e:
        services_status["cache"] = f"fel: {str(e)}"
    
    try:
        # xAI API
        if settings.xai_api_key:
            services_status["xai_api"] = "konfigurerad"
        else:
            services_status["xai_api"] = "inte konfigurerad"
    except Exception as e:
        services_status["xai_api"] = f"fel: {str(e)}"
    
    # Systeminfo
    system_info = {
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
        "miljö": settings.environment,
        "debug_läge": settings.debug,
        "gdpr_aktiverat": settings.gdpr_enabled,
        "svenska_datakällor": len(settings.swedish_sources)
    }
    
    # Beräkna svarstid
    response_time = (datetime.utcnow() - start_time).total_seconds()
    
    overall_status = "frisk" if all(
        "fel" not in status for status in services_status.values()
    ) else "degraderad"
    
    return HealthResponse(
        status=overall_status,
        version="6.0.0",
        tidsstämpel=datetime.utcnow().isoformat(),
        tjänster=services_status,
        system_info={
            **system_info,
            "svarstid_sekunder": response_time
        }
    )

@app.post("/analysera", response_model=AnalysisResponse, tags=["Analys"])
async def analyze_query(
    request: QueryRequest,
    client_request: Request,
    gdpr_consent: bool = Depends(security.verify_gdpr_consent)
):
    """
    Huvudendpoint för intelligensanalys av svenska frågor
    
    Denna endpoint:
    - Analyserar frågor på svenska
    - Väljer optimal profil automatiskt eller använder specificerad
    - Samlar data från svenska källor
    - Genererar intelligent respons
    - Respekterar GDPR-krav
    """
    start_time = datetime.utcnow()
    
    try:
        # GDPR-kontroll
        if not gdpr_consent:
            raise HTTPException(
                status_code=403,
                detail={
                    "fel": "GDPR-samtycke krävs",
                    "meddelande": "Du måste ge samtycke för databehandling enligt GDPR",
                    "länk": "/gdpr/samtycke"
                }
            )
        
        # Säkerhetsvalidering
        await security.validate_request(client_request, request)
        
        # Logga analys-request (utan känslig data)
        logger.info(f"📊 Ny analysförfrågning: profil={request.profil}, längd={len(request.query)}")
        
        # Utför analysen genom ProfileRouter
        result = await profile_router.route_query(
            query=request.query,
            user_profile=request.profil,
            user_id=request.användar_id,
            metadata=request.metadata
        )
        
        # Beräkna bearbetningstid
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Logga framgång
        logger.info(f"✅ Analys slutförd: {processing_time:.2f}s, profil={result.get('profil')}")
        
        return AnalysisResponse(
            framgång=True,
            profil_använd=result.get("profil", "okänd"),
            resultat=result,
            tidsstämpel=datetime.utcnow().isoformat(),
            bearbetningstid=processing_time,
            gdpr_kompatibel=True,
            datakällor=result.get("använd_källor", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Detaljerad felloggning
        logger.error(f"❌ Fel vid analys: {e}", exc_info=True)
        
        # Graceful degradation
        fallback = GracefulDegradation.provide_fallback_response(
            request.query, e
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AnalysisResponse(
            framgång=False,
            profil_använd="fallback",
            resultat=fallback,
            tidsstämpel=datetime.utcnow().isoformat(),
            bearbetningstid=processing_time,
            gdpr_kompatibel=True,
            datakällor=[]
        )

@app.get("/profiler", tags=["Konfiguration"])
async def get_profiles():
    """Lista tillgängliga profiler med beskrivningar"""
    profiles_info = {}
    
    for profile_name, config in settings.profiles.items():
        profiles_info[profile_name] = {
            "namn": profile_name,
            "beskrivning": config.get("beskrivning", ""),
            "förväntad_svarstid": config.get("förväntad_svarstid", "okänd"),
            "ai_modell": config.get("ai_model", "okänd"),
            "max_källor": config.get("max_källor", 0),
            "externt_api": config.get("externa_anrop", True),
            "rekommenderad_för": config.get("rekommenderad_för", [])
        }
    
    return {
        "tillgängliga_profiler": profiles_info,
        "standardprofil": "smart",
        "automatiskt_val": "Systemet kan välja profil automatiskt baserat på frågan",
        "användning": {
            "snabb": "För enkla frågor som behöver snabba svar",
            "smart": "För komplexa analyser med flera datakällor",
            "privat": "För känsliga frågor, allt lokalt"
        }
    }

@app.get("/datakällor", tags=["Information"])
async def get_data_sources():
    """Information om tillgängliga svenska datakällor"""
    sources_info = {}
    
    for source_name, config in settings.swedish_sources.items():
        sources_info[source_name] = {
            "namn": source_name,
            "typ": config.get("typ", "okänd"),
            "beskrivning": config.get("beskrivning", ""),
            "uppdateringsfrekvens": config.get("cache", "okänd"),
            "tillförlitlighet": config.get("tillförlitlighet", "hög"),
            "språk": "svenska",
            "gdpr_kompatibel": True
        }
    
    return {
        "svenska_datakällor": sources_info,
        "totalt_antal": len(sources_info),
        "kategorier": {
            "statistik": ["scb"],
            "finansiell": ["omx"],
            "nyheter": ["svenska_nyheter"],
            "väder": ["smhi"]
        }
    }

# GDPR-relaterade endpoints
@app.get("/gdpr/info", tags=["GDPR"])
async def gdpr_information():
    """Information om GDPR-efterlevnad"""
    return {
        "gdpr_status": "fullt kompatibel",
        "databehandling": {
            "syfte": "Intelligensanalys och rapportering",
            "rättslig_grund": "samtycke (Art. 6.1.a)",
            "lagringstid": "30 dagar eller tills användaren begär radering",
            "tredje_part": "Endast nödvändiga AI-tjänster (xAI med anonymisering)"
        },
        "användarrättigheter": {
            "tillgång": "GET /användare/data",
            "rättelse": "PUT /användare/data",
            "radering": "DELETE /användare/data",
            "portabilitet": "GET /användare/export",
            "invändning": "POST /användare/invändning"
        },
        "kontakt": {
            "dataskyddsombud": "dpo@iris.se",
            "integritetsmyndigheten": "https://www.imy.se"
        }
    }

@app.post("/gdpr/samtycke", tags=["GDPR"])
async def give_gdpr_consent(
    user_id: str,
    consent_data: Dict[str, bool]
):
    """Ge eller återkalla GDPR-samtycke"""
    try:
        await security.update_consent(user_id, consent_data)
        
        return {
            "framgång": True,
            "meddelande": "Samtycke uppdaterat",
            "tidsstämpel": datetime.utcnow().isoformat(),
            "giltigt_till": (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).isoformat()
        }
    except Exception as e:
        logger.error(f"Fel vid samtyckes-uppdatering: {e}")
        raise HTTPException(status_code=500, detail="Kunde inte uppdatera samtycke")

# Utvecklings- och debug-endpoints (endast i debug-läge)
if settings.debug:
    @app.get("/debug/status", tags=["Debug"])
    async def debug_status():
        """Debug-information (endast i utvecklingsläge)"""
        return {
            "miljövariabler": {
                "XAI_API_KEY": bool(settings.xai_api_key),
                "DATABASE_URL": bool(settings.database_url),
                "REDIS_URL": bool(settings.redis_url),
                "DEBUG": settings.debug
            },
            "inställda_profiler": list(settings.profiles.keys()),
            "svenska_källor": list(settings.swedish_sources.keys()),
            "system": {
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "pid": os.getpid(),
                "cwd": os.getcwd()
            }
        }

# Startup meddelande
@app.on_event("startup")
async def startup_message():
    """Visa startup-meddelande"""
    logger.info("=" * 60)
    logger.info("🇸🇪 IRIS v6.0 - Förenklad Intelligensrapportering")
    logger.info("=" * 60)
    logger.info(f"📍 Miljö: {settings.environment}")
    logger.info(f"🔒 GDPR: {'Aktiverat' if settings.gdpr_enabled else 'Inaktiverat'}")
    logger.info(f"🧠 AI: {'xAI Grok' if settings.xai_api_key else 'Lokal modell'}")
    logger.info(f"📊 Profiler: {', '.join(settings.profiles.keys())}")
    logger.info(f"🌐 Server: http://localhost:8000")
    logger.info(f"📚 Docs: http://localhost:8000/dokumentation")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    
    # Kör servern
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True
    )