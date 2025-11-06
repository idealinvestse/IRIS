"""
IRIS v6.0 - Robust Felhantering och Circuit Breaker
Avancerad felhantering för svenska datakällor och externa API:er
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional, List
from enum import Enum
import functools
import json
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"     # Normal operation
    OPEN = "open"         # Failing, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Konfiguration för circuit breaker"""
    failure_threshold: int = 5        # Antal fel innan öppning
    timeout_seconds: int = 60         # Timeout innan test
    recovery_threshold: int = 3       # Antal framgångar för återställning
    max_failures_per_window: int = 10  # Max fel per tidsperiod
    window_seconds: int = 300         # Tidsperiod för fel-räkning

@dataclass
class FailureRecord:
    """Registrerar fel för statistik"""
    timestamp: datetime
    error_type: str
    error_message: str
    service_name: str

class CircuitBreaker:
    """
    Robust circuit breaker för svenska datakällor
    Skyddar mot överdrivet API-användning och hantera tjänstefel
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.failure_history: List[FailureRecord] = []
        
        logger.info(f"🔌 Circuit breaker '{name}' initialiserad")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Utför anrop genom circuit breaker"""
        
        # Kontrollera state innan anrop
        if not self._can_attempt():
            raise CircuitBreakerOpenException(
                f"Circuit breaker '{self.name}' är öppen. Senaste fel: {self.last_failure_time}"
            )
        
        try:
            # Försök anropet
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Registrera framgång
            self._record_success(execution_time)
            
            return result
            
        except Exception as e:
            # Registrera fel
            self._record_failure(e)
            raise
    
    def _can_attempt(self) -> bool:
        """Kontrollera om anrop är tillåtet baserat på aktuell state"""
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # Kontrollera om timeout har passerat
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.config.timeout_seconds)):
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"🟡 Circuit breaker '{self.name}' övergår till HALF_OPEN")
                return True
            return False
        
        return False
    
    def _record_success(self, execution_time: float):
        """Registrera framgångsrikt anrop"""
        self.success_count += 1
        self.last_success_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.success_count >= self.config.recovery_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info(f"✅ Circuit breaker '{self.name}' återställd till CLOSED")
        
        # Rensa gamla fel från historiken
        self._cleanup_old_failures()
        
        logger.debug(f"✅ Framgång för '{self.name}': {execution_time:.2f}s")
    
    def _record_failure(self, error: Exception):
        """Registrera misslyckat anrop"""
        now = datetime.now()
        self.failure_count += 1
        self.last_failure_time = now
        
        # Lägg till i historik
        failure_record = FailureRecord(
            timestamp=now,
            error_type=type(error).__name__,
            error_message=str(error),
            service_name=self.name
        )
        self.failure_history.append(failure_record)
        
        # Rensa gamla fel
        self._cleanup_old_failures()
        
        # Kontrollera om vi ska öppna circuit breaker
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0
            logger.warning(f"🔴 Circuit breaker '{self.name}' ÖPPNAD efter {self.failure_count} fel")
        
        logger.error(f"❌ Fel för '{self.name}': {type(error).__name__}: {error}")
    
    def _cleanup_old_failures(self):
        """Ta bort gamla fel från historiken"""
        cutoff_time = datetime.now() - timedelta(seconds=self.config.window_seconds)
        self.failure_history = [
            f for f in self.failure_history 
            if f.timestamp > cutoff_time
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Hämta statistik om circuit breaker"""
        recent_failures = len(self.failure_history)
        
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "recent_failures": recent_failures,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success": self.last_success_time.isoformat() if self.last_success_time else None,
            "failure_rate": recent_failures / max(1, recent_failures + self.success_count) * 100
        }

class CircuitBreakerOpenException(Exception):
    """Exception när circuit breaker är öppen"""
    pass

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Decorator för retry med exponentiell backoff
    Optimerad för svenska API:ers rate limits
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Sista försöket - ge upp
                    if attempt == max_retries:
                        logger.error(f"🚫 Alla {max_retries} återförsök misslyckades för {func.__name__}: {e}")
                        raise
                    
                    # Beräkna väntetid med exponentiell backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Lägg till jitter för att undvika thundering herd
                    if jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"⏳ Försök {attempt + 1}/{max_retries} misslyckades för {func.__name__}, väntar {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
            
            raise last_exception
            
        return wrapper
    return decorator

class GracefulDegradation:
    """
    Hantera graceful degradation när svenska tjänster är otillgängliga
    Ger användbar fallback-information
    """
    
    @staticmethod
    def provide_fallback_response(query: str, error: Exception) -> Dict[str, Any]:
        """
        Ge en användbar fallback-respons på svenska
        """
        error_type = type(error).__name__
        current_time = datetime.now()
        
        # Skapa användbart fallback-svar baserat på fel-typ
        fallback_content = GracefulDegradation._generate_fallback_content(query, error_type)
        
        return {
            "typ": "fallback",
            "meddelande": f"Tjänsten är tillfälligt otillgänglig. Här är vad vi vet:",
            "fallback_svar": fallback_content,
            "original_fråga": query,
            "fel_typ": error_type,
            "fel_meddelande": str(error)[:200],  # Begränsa längd
            "tidsstämpel": current_time.isoformat(),
            "status": "degraded",
            "nästa_försök": (current_time + timedelta(minutes=5)).isoformat(),
            "rekommendation": "Försök igen om några minuter eller kontakta support om problemet kvarstår."
        }
    
    @staticmethod
    def _generate_fallback_content(query: str, error_type: str) -> str:
        """Generera innehållsrikt fallback-svar baserat på fråga"""
        
        # Enkel intent-igenkänning för svenska frågor
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["väder", "temperatur", "regn", "sol"]):
            return (
                "Väderinformation är tillfälligt otillgänglig. "
                "Du kan kontrollera SMHI.se direkt eller försöka igen senare."
            )
        
        elif any(word in query_lower for word in ["aktie", "omx", "börsen", "kurs"]):
            return (
                "Finansiell information är tillfälligt otillgänglig. "
                "Kontrollera Avanza, Nordnet eller Stockholmsbörsen direkt."
            )
        
        elif any(word in query_lower for word in ["nyheter", "nyhet", "aktuellt"]):
            return (
                "Nyhetsuppdateringar är tillfälligt otillgängliga. "
                "Besök SVT.se, DN.se eller Aftonbladet.se för senaste nyheterna."
            )
        
        elif any(word in query_lower for word in ["statistik", "scb", "befolkning", "siffror"]):
            return (
                "Statistisk information från SCB är tillfälligt otillgänglig. "
                "Besök SCB.se direkt för officiell svensk statistik."
            )
        
        else:
            return (
                f"Kunde inte behandla din fråga '{query}' just nu på grund av tekniska problem. "
                "Våra system arbetar för att lösa problemet. Försök igen om några minuter."
            )
    
    @staticmethod
    async def get_cached_response(cache_key: str, redis_client=None) -> Optional[Dict[str, Any]]:
        """Hämta cachad respons som fallback"""
        if not redis_client:
            return None
        
        try:
            cached_data = await redis_client.get(f"fallback:{cache_key}")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Kunde inte hämta fallback från cache: {e}")
        
        return None
    
    @staticmethod
    async def save_fallback_cache(cache_key: str, data: Dict[str, Any], redis_client=None, ttl: int = 3600):
        """Spara data som fallback i cache"""
        if not redis_client:
            return
        
        try:
            await redis_client.setex(
                f"fallback:{cache_key}",
                ttl,
                json.dumps(data, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"Kunde inte spara fallback till cache: {e}")

class ErrorAnalyzer:
    """
    Analyserar fel-mönster för svenska datakällor
    Hjälper till att identifiera och förutsäga problem
    """
    
    def __init__(self):
        self.error_patterns: Dict[str, List[FailureRecord]] = {}
    
    def analyze_error_pattern(self, service_name: str, failures: List[FailureRecord]) -> Dict[str, Any]:
        """Analysera felmönster för en tjänst"""
        if not failures:
            return {"pattern": "no_failures", "severity": "low"}
        
        # Gruppera fel per typ
        error_types = {}
        for failure in failures:
            error_type = failure.error_type
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(failure)
        
        # Analysera trender
        recent_failures = [f for f in failures if 
                         datetime.now() - f.timestamp < timedelta(hours=1)]
        
        severity = "low"
        if len(recent_failures) > 10:
            severity = "critical"
        elif len(recent_failures) > 5:
            severity = "high"
        elif len(recent_failures) > 2:
            severity = "medium"
        
        return {
            "service": service_name,
            "total_failures": len(failures),
            "recent_failures": len(recent_failures),
            "error_types": list(error_types.keys()),
            "most_common_error": max(error_types.items(), key=lambda x: len(x[1]))[0] if error_types else None,
            "severity": severity,
            "recommendation": self._get_recommendation(severity, error_types)
        }
    
    def _get_recommendation(self, severity: str, error_types: Dict) -> str:
        """Ge rekommendationer baserat på fel-analys"""
        if severity == "critical":
            return "Stäng av tjänsten temporärt och kontakta systemadministratör"
        elif severity == "high":
            return "Öka retry-delays och minska load på tjänsten"
        elif severity == "medium":
            return "Övervaka noga och förbered fallback-strategier"
        else:
            return "Fortsätt normal operation med standard övervakning"

# Globala circuit breakers för svenska tjänster
SWEDISH_CIRCUIT_BREAKERS = {
    "scb": CircuitBreaker("SCB", CircuitBreakerConfig(failure_threshold=3, timeout_seconds=120)),
    "omx": CircuitBreaker("OMX", CircuitBreakerConfig(failure_threshold=5, timeout_seconds=60)),
    "news": CircuitBreaker("News", CircuitBreakerConfig(failure_threshold=4, timeout_seconds=90)),
    "smhi": CircuitBreaker("SMHI", CircuitBreakerConfig(failure_threshold=3, timeout_seconds=180)),
    "xai": CircuitBreaker("xAI", CircuitBreakerConfig(failure_threshold=5, timeout_seconds=300))
}

def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Hämta circuit breaker för en tjänst"""
    return SWEDISH_CIRCUIT_BREAKERS.get(service_name.lower(), 
                                       CircuitBreaker(service_name))

async def get_all_circuit_breaker_stats() -> Dict[str, Dict[str, Any]]:
    """Hämta statistik för alla circuit breakers"""
    stats = {}
    for name, breaker in SWEDISH_CIRCUIT_BREAKERS.items():
        stats[name] = breaker.get_statistics()
    return stats

# Hjälpfunktioner för felsökning
def log_error_context(error: Exception, context: Dict[str, Any]):
    """Logga fel med kontext för debugging"""
    logger.error(
        f"🐛 Fel i kontext: {type(error).__name__}: {error}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Testa circuit breaker
    async def test_circuit_breaker():
        breaker = CircuitBreaker("test")
        
        async def failing_function():
            raise Exception("Test error")
        
        # Testa flera fel
        for i in range(7):
            try:
                await breaker.call(failing_function)
            except:
                print(f"Försök {i+1} misslyckades")
        
        # Visa statistik
        stats = breaker.get_statistics()
        print(f"Circuit breaker stats: {stats}")
    
    asyncio.run(test_circuit_breaker())