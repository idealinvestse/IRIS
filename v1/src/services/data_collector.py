"""
IRIS v6.0 - Data Collector
Robust datainhämtning från svenska datakällor med circuit breakers
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Samlar data från svenska datakällor med robust felhantering
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        logger.info("📡 DataCollector initialiserad")
    
    async def collect_data(
        self,
        query: str,
        sources: List[str],
        profile_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Samla data från svenska källor parallellt
        """
        logger.info(f"📊 Samlar data från {len(sources)} källor")
        
        # Importera svenska källor
        from src.services.swedish_sources import SwedishSources
        swedish = SwedishSources()
        
        # Samla data parallellt från alla källor
        tasks = []
        for source_name in sources:
            task = self._collect_from_source(source_name, query, swedish)
            tasks.append(task)
        
        # Vänta på alla källor (eller timeout)
        max_wait = profile_config.get("max_källor", 5) * 2  # 2 sekunder per källa
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrera ut fel och samla lyckade resultat
        collected = {}
        for source_name, result in zip(sources, results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️ Fel från {source_name}: {result}")
                collected[source_name] = {"error": str(result), "available": False}
            else:
                collected[source_name] = result
        
        return collected
    
    async def _collect_from_source(
        self,
        source_name: str,
        query: str,
        swedish_sources
    ) -> Dict[str, Any]:
        """
        Samla data från en specifik källa med circuit breaker
        """
        from src.utils.error_handling import get_circuit_breaker
        
        breaker = get_circuit_breaker(source_name)
        
        try:
            # Anropa genom circuit breaker
            if source_name == "scb":
                data = await breaker.call(swedish_sources.get_scb_data, query)
            elif source_name == "omx":
                data = await breaker.call(swedish_sources.get_omx_data)
            elif source_name == "svenska_nyheter":
                data = await breaker.call(swedish_sources.get_swedish_news, query)
            elif source_name == "smhi":
                data = await breaker.call(swedish_sources.get_smhi_data, query)
            else:
                data = {"error": f"Okänd källa: {source_name}"}
            
            return data
            
        except Exception as e:
            logger.error(f"Fel vid datahämtning från {source_name}: {e}")
            raise
