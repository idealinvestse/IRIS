"""
IRIS v6.0 - Konfigurationshantering
Centralized configuration management för svenska datakällor och AI-profiler
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Huvudkonfiguration för IRIS v6.0"""
    
    # Miljöinställningar
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Databas
    database_url: str = Field(default="sqlite:///./iris.db", env="DATABASE_URL")
    
    # Cache
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl_default: int = Field(default=3600, env="CACHE_TTL_DEFAULT")
    
    # AI och xAI
    xai_api_key: Optional[str] = Field(default=None, env="XAI_API_KEY")
    xai_base_url: str = Field(default="https://api.x.ai/v1", env="XAI_BASE_URL")
    xai_timeout: int = Field(default=30, env="XAI_TIMEOUT")
    
    # GDPR
    gdpr_enabled: bool = Field(default=True, env="GDPR_ENABLED")
    data_retention_days: int = Field(default=30, env="DATA_RETENTION_DAYS")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Svenska API nycklar
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Säkerhet
    secret_key: str = Field(default="iris-dev-key-change-in-prod", env="SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # Lokalisering
    default_language: str = Field(default="sv", env="DEFAULT_LANGUAGE")
    timezone: str = Field(default="Europe/Stockholm", env="TIMEZONE")
    
    # Profiler och källor (laddas från YAML)
    profiles: Dict[str, Any] = {}
    swedish_sources: Dict[str, Any] = {}
    source_cache_ttl: Dict[str, int] = {}
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_profiles()
        self._load_swedish_sources()
        self._setup_logging()
    
    def _load_profiles(self):
        """Ladda AI-profiler från konfigurationsfil"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "../../config/profiles.yaml")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.profiles = config.get('profiles', {})
            else:
                # Fallback till inbyggda profiler
                self.profiles = self._get_default_profiles()
            
            logger.info(f"✅ Laddade {len(self.profiles)} AI-profiler")
            
        except Exception as e:
            logger.warning(f"⚠️ Kunde inte ladda profiles.yaml: {e}")
            self.profiles = self._get_default_profiles()
    
    def _load_swedish_sources(self):
        """Ladda svenska datakällkonfigurationer"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "../../config/sources.yaml")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.swedish_sources = config.get('svenska_källor', {})
                    
                    # Extrahera cache TTL:er
                    self.source_cache_ttl = {
                        name: source.get('cache', 3600)
                        for name, source in self.swedish_sources.items()
                    }
            else:
                self.swedish_sources = self._get_default_sources()
                self.source_cache_ttl = {name: 3600 for name in self.swedish_sources.keys()}
            
            logger.info(f"✅ Laddade {len(self.swedish_sources)} svenska datakällor")
            
        except Exception as e:
            logger.warning(f"⚠️ Kunde inte ladda sources.yaml: {e}")
            self.swedish_sources = self._get_default_sources()
    
    def _setup_logging(self):
        """Konfigurera logging-nivå"""
        logging.getLogger().setLevel(getattr(logging, self.log_level.upper(), logging.INFO))
    
    def _get_default_profiles(self) -> Dict[str, Any]:
        """Standard AI-profiler om YAML-fil saknas"""
        return {
            "snabb": {
                "beskrivning": "Snabba svar under 2 sekunder",
                "ai_model": "grok-4-turbo",
                "max_källor": 2,
                "cache_ttl": 300,
                "förväntad_svarstid": "< 2 sekunder",
                "externa_anrop": True,
                "rekommenderad_för": ["enkla frågor", "real-time data"]
            },
            "smart": {
                "beskrivning": "Balanserad analys med flera källor",
                "ai_model": "grok-4",
                "max_källor": 5,
                "cache_ttl": 600,
                "förväntad_svarstid": "3-7 sekunder",
                "externa_anrop": True,
                "rekommenderad_för": ["komplexa analyser", "djup insikt"]
            },
            "privat": {
                "beskrivning": "Helt lokal bearbetning utan externa API:er",
                "ai_model": "llama-3-local",
                "max_källor": 3,
                "cache_ttl": 1800,
                "förväntad_svarstid": "5-15 sekunder",
                "externa_anrop": False,
                "rekommenderad_för": ["känslig data", "GDPR-strikt"]
            }
        }
    
    def _get_default_sources(self) -> Dict[str, Any]:
        """Standard svenska datakällor"""
        return {
            "scb": {
                "namn": "Statistiska centralbyrån",
                "url": "https://api.scb.se/OV0104/v1/doris/sv/ssd/",
                "typ": "statistik",
                "beskrivning": "Officiell svensk statistik",
                "cache": 3600,
                "tillförlitlighet": "mycket hög",
                "språk": "svenska",
                "gdpr_kompatibel": True,
                "kräver_api_nyckel": False
            },
            "omx": {
                "namn": "OMX Stockholm",
                "url": "https://query1.finance.yahoo.com/v8/finance/chart/^OMX",
                "typ": "finansiell",
                "beskrivning": "Stockholmsbörsens huvudindex",
                "cache": 300,
                "tillförlitlighet": "hög",
                "språk": "engelska/svenska",
                "gdpr_kompatibel": True,
                "kräver_api_nyckel": False
            },
            "svenska_nyheter": {
                "namn": "Svenska Nyheter",
                "url": "https://newsdata.io/api/1/news",
                "typ": "nyheter",
                "beskrivning": "Aktuella svenska nyheter",
                "cache": 900,
                "tillförlitlighet": "medel-hög",
                "språk": "svenska",
                "gdpr_kompatibel": True,
                "kräver_api_nyckel": True,
                "api_nyckel_env": "NEWS_API_KEY"
            },
            "smhi": {
                "namn": "SMHI Väderdata",
                "url": "https://opendata-download-metfcst.smhi.se/api",
                "typ": "väder",
                "beskrivning": "Officiell svensk väderdata",
                "cache": 1800,
                "tillförlitlighet": "mycket hög",
                "språk": "svenska",
                "gdpr_kompatibel": True,
                "kräver_api_nyckel": False
            }
        }
    
    def get_profile_config(self, profile_name: str) -> Dict[str, Any]:
        """Hämta konfiguration för specifik profil"""
        return self.profiles.get(profile_name, self.profiles.get("smart", {}))
    
    def get_source_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Hämta konfiguration för specifik datakälla"""
        return self.swedish_sources.get(source_name)
    
    def get_sources_for_profile(self, profile_name: str) -> List[str]:
        """Hämta lämpliga datakällor för en profil"""
        profile_config = self.get_profile_config(profile_name)
        max_sources = profile_config.get("max_källor", 3)
        external_calls_allowed = profile_config.get("externa_anrop", True)
        
        available_sources = []
        
        for source_name, source_config in self.swedish_sources.items():
            # För privat profil, undvik källor som kräver externa API:er
            if not external_calls_allowed and source_config.get("kräver_api_nyckel", False):
                continue
            
            # Prioritera högre tillförlitlighet
            if source_config.get("tillförlitlighet") in ["mycket hög", "hög"]:
                available_sources.append(source_name)
        
        # Begränsa till max antal källor
        return available_sources[:max_sources]
    
    def is_production(self) -> bool:
        """Kontrollera om vi kör i produktionsmiljö"""
        return self.environment.lower() == "production"
    
    def get_cache_ttl(self, source_name: str) -> int:
        """Hämta cache TTL för en datakälla"""
        return self.source_cache_ttl.get(source_name, self.cache_ttl_default)

@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance - skapar endast en instans per process
    """
    return Settings()

# Hjälpfunktioner för konfigurationsvalidering
def validate_configuration() -> Dict[str, Any]:
    """Validera att all nödvändig konfiguration är korrekt"""
    settings = get_settings()
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": []
    }
    
    # Kontrollera kritiska inställningar
    if settings.environment == "production":
        if settings.secret_key == "iris-dev-key-change-in-prod":
            validation_results["errors"].append("SECRET_KEY måste ändras i produktion")
            validation_results["valid"] = False
        
        if not settings.encryption_key:
            validation_results["warnings"].append("ENCRYPTION_KEY bör sättas för säker datalagring")
    
    # Kontrollera AI-konfiguration
    if not settings.xai_api_key and not any("local" in p.get("ai_model", "") for p in settings.profiles.values()):
        validation_results["warnings"].append("Varken xAI API-nyckel eller lokal AI-modell konfigurerad")
    
    # Kontrollera svenska API:er
    for source_name, source_config in settings.swedish_sources.items():
        if source_config.get("kräver_api_nyckel", False):
            api_key_env = source_config.get("api_nyckel_env")
            if api_key_env and not os.getenv(api_key_env):
                validation_results["warnings"].append(f"API-nyckel saknas för {source_name} ({api_key_env})")
    
    # Info om konfiguration
    validation_results["info"].extend([
        f"Miljö: {settings.environment}",
        f"GDPR aktiverat: {settings.gdpr_enabled}",
        f"Profiler: {', '.join(settings.profiles.keys())}",
        f"Svenska källor: {', '.join(settings.swedish_sources.keys())}"
    ])
    
    return validation_results

def print_configuration_summary():
    """Skriv ut sammanfattning av aktuell konfiguration"""
    settings = get_settings()
    validation = validate_configuration()
    
    print("\n" + "="*60)
    print("🇸🇪 IRIS v6.0 - Konfigurationssammanfattning")
    print("="*60)
    
    print(f"📍 Miljö: {settings.environment}")
    print(f"🔒 GDPR: {'✅' if settings.gdpr_enabled else '❌'}")
    print(f"🧠 xAI: {'✅' if settings.xai_api_key else '❌'}")
    print(f"💾 Databas: {settings.database_url}")
    print(f"🚀 Cache: {'Redis' if settings.redis_url else 'Ingen'}")
    
    print(f"\n📊 AI-Profiler ({len(settings.profiles)}):")
    for name, config in settings.profiles.items():
        print(f"  • {name}: {config.get('beskrivning', 'Ingen beskrivning')}")
    
    print(f"\n🌐 Svenska Datakällor ({len(settings.swedish_sources)}):")
    for name, config in settings.swedish_sources.items():
        status = "✅" if not config.get("kräver_api_nyckel") else ("✅" if os.getenv(config.get("api_nyckel_env", "")) else "⚠️")
        print(f"  • {name} ({config.get('typ')}): {status}")
    
    if validation["errors"]:
        print(f"\n❌ Fel ({len(validation['errors'])}):")
        for error in validation["errors"]:
            print(f"  • {error}")
    
    if validation["warnings"]:
        print(f"\n⚠️  Varningar ({len(validation['warnings'])}):")
        for warning in validation["warnings"]:
            print(f"  • {warning}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    # Testa konfiguration
    print_configuration_summary()
    validation = validate_configuration()
    print(f"Konfiguration giltig: {'✅' if validation['valid'] else '❌'}")