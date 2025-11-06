"""
IRIS v6.0 - AI Provider Factory
Factory pattern för att skapa AI-providers
"""

import logging
from typing import Optional
from .base import BaseAIProvider
from .groq_provider import GroqProvider
from .xai_provider import XAIProvider
from .local_provider import LocalProvider

logger = logging.getLogger(__name__)

class AIProviderFactory:
    """
    Factory för att skapa AI-providers baserat på konfiguration
    """
    
    @staticmethod
    def create_provider(
        provider_name: str,
        settings
    ) -> Optional[BaseAIProvider]:
        """
        Skapa AI-provider baserat på namn
        
        Args:
            provider_name: Namnet på providern (groq, xai, lokal)
            settings: Settings-objekt med API-nycklar och konfiguration
            
        Returns:
            BaseAIProvider instance eller None om provider inte kan skapas
        """
        provider_name = provider_name.lower()
        
        logger.info(f"🏭 Skapar AI provider: {provider_name}")
        
        if provider_name == "groq":
            if not settings.groq_api_key:
                logger.warning("⚠️ Groq API-nyckel saknas, kan inte skapa GroqProvider")
                return None
            
            return GroqProvider(
                api_key=settings.groq_api_key,
                timeout=settings.groq_timeout
            )
        
        elif provider_name == "xai":
            if not settings.xai_api_key:
                logger.warning("⚠️ xAI API-nyckel saknas, kan inte skapa XAIProvider")
                return None
            
            return XAIProvider(
                api_key=settings.xai_api_key,
                base_url=settings.xai_base_url,
                timeout=settings.xai_timeout
            )
        
        elif provider_name == "lokal":
            # Lokal provider behöver inga API-nycklar
            return LocalProvider()
        
        else:
            logger.error(f"❌ Okänd AI provider: {provider_name}")
            return None
    
    @staticmethod
    def get_available_providers(settings) -> list:
        """
        Returnera lista över tillgängliga providers baserat på konfiguration
        
        Returns:
            List av provider-namn som är tillgängliga
        """
        available = []
        
        if settings.groq_api_key:
            available.append("groq")
        
        if settings.xai_api_key:
            available.append("xai")
        
        # Lokal är alltid tillgänglig
        available.append("lokal")
        
        logger.info(f"📋 Tillgängliga providers: {', '.join(available)}")
        
        return available
