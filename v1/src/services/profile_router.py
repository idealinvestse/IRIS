"""
IRIS v6.0 - Profile Router
Intelligent dirigering till optimal AI-profil baserat på fråga och kontext
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfileRouter:
    """
    Dirigerar frågor till optimal AI-profil baserat på komplexitet och krav
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        logger.info("🧭 ProfileRouter initialiserad")
    
    async def route_query(
        self,
        query: str,
        user_profile: Optional[str] = None,
        user_id: str = "anonym",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Hantera fråga genom optimal profil
        """
        start_time = datetime.utcnow()
        
        # Välj profil
        selected_profile = user_profile or self._select_optimal_profile(query)
        
        logger.info(f"📊 Vald profil: {selected_profile} för fråga (längd: {len(query)})")
        
        try:
            # Hämta profil-konfiguration
            profile_config = self.settings.get_profile_config(selected_profile)
            
            # Samla data från svenska källor
            from src.services.data_collector import DataCollector
            collector = DataCollector()
            sources = self.settings.get_sources_for_profile(selected_profile)
            
            collected_data = await collector.collect_data(query, sources, profile_config)
            
            # Analysera med AI
            from src.services.ai_analyzer import AIAnalyzer
            analyzer = AIAnalyzer()
            
            analysis_result = await analyzer.analyze(
                query=query,
                context_data=collected_data,
                profile=selected_profile,
                profile_config=profile_config
            )
            
            # Beräkna totaltid
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Logga till databas (GDPR-kompatibelt)
            await self._log_query(
                user_id=user_id,
                query=query,
                profile=selected_profile,
                sources=sources,
                processing_time=int(processing_time * 1000),
                success=True
            )
            
            return {
                "profil": selected_profile,
                "resultat": analysis_result,
                "använd_källor": sources,
                "bearbetningstid": processing_time,
                "metadata": {
                    "profil_config": profile_config.get("beskrivning"),
                    "antal_källor": len(sources)
                }
            }
            
        except Exception as e:
            logger.error(f"Fel i profile routing: {e}", exc_info=True)
            
            # Logga fel
            await self._log_query(
                user_id=user_id,
                query=query,
                profile=selected_profile,
                sources=[],
                processing_time=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                success=False
            )
            
            raise
    
    def _select_optimal_profile(self, query: str) -> str:
        """
        Välj optimal profil baserat på fråga-analys
        """
        query_lower = query.lower()
        
        # Privat profil för känsliga frågor
        private_keywords = ["privat", "personlig", "känslig", "konfidentiell", "hemlig"]
        if any(keyword in query_lower for keyword in private_keywords):
            return "privat"
        
        # Snabb profil för enkla frågor
        quick_keywords = ["vad är", "hur mycket", "när", "var", "vem"]
        if any(query_lower.startswith(keyword) for keyword in quick_keywords) and len(query) < 100:
            return "snabb"
        
        # Smart profil för komplexa analyser
        complex_keywords = ["analysera", "jämför", "förklara", "beskriv", "utvärdera", "bedöm"]
        if any(keyword in query_lower for keyword in complex_keywords):
            return "smart"
        
        # Default till smart
        return "smart"
    
    async def _log_query(
        self,
        user_id: str,
        query: str,
        profile: str,
        sources: list,
        processing_time: int,
        success: bool
    ):
        """Logga fråga till databas"""
        try:
            from src.core.database import Database
            from src.core.security import SecurityManager
            
            db = Database()
            security = SecurityManager()
            
            # Hash query för GDPR
            query_hash = security.hash_query(query)
            
            # Kontrollera GDPR-samtycke
            gdpr_consent = await security.verify_gdpr_consent(user_id)
            
            await db.log_query(
                user_id=user_id,
                query_hash=query_hash,
                profile=profile,
                sources=sources,
                processing_time=processing_time,
                success=success,
                gdpr_consent=gdpr_consent
            )
            
        except Exception as e:
            logger.warning(f"Kunde inte logga fråga: {e}")
