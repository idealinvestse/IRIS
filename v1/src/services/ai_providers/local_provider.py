"""
IRIS v6.0 - Local AI Provider
Regelbaserad lokal AI utan externa API:er
"""

import logging
from typing import Dict, Any, AsyncIterator
from .base import BaseAIProvider

logger = logging.getLogger(__name__)

class LocalProvider(BaseAIProvider):
    """
    Lokal regelbaserad AI provider
    Används för privat profil och som sista fallback
    """
    
    def __init__(self):
        logger.info("💻 LocalProvider initialiserad")
    
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
        """
        Enkel lokal analys utan externa API:er
        
        Args:
            query: Användarens fråga
            context: Kontext från datakällor
            model: AI-modell att använda
            temperature: Kreativitetsnivå (0.0-1.0)
            max_tokens: Max antal tokens i svaret
            stream: Om streaming ska användas
            
        Returns:
            Dict med svar, modell, provider, etc.
        """
        try:
            # Input validation
            if query is None:
                query = ""
            
            if context is None:
                context = ""
            
            logger.info("💻 Använder lokal regelbaserad analys")
            
            response_parts = [
                f"Baserat på din fråga '{query}' och tillgängliga svenska källor:"
            ]
            
            # Analysera kontext
            if context:
                context_lower = context.lower()
                
                if "omx" in context_lower or "finansiell" in context_lower:
                    response_parts.append("- Finansiell data från OMX Stockholm visar aktuell börsaktivitet.")
                
                if "scb" in context_lower or "statistik" in context_lower:
                    response_parts.append("- Statistik från SCB ger officiella svenska siffror.")
                
                if "smhi" in context_lower or "väder" in context_lower:
                    response_parts.append("- Väderdata från SMHI ger prognoser för Sverige.")
                
                if "nyheter" in context_lower or "news" in context_lower:
                    response_parts.append("- Aktuella nyheter från svenska medier.")
            
            # Lägg till info om begränsningar
            response_parts.append("\nOBS: Detta är en lokal regelbaserad analys.")
            response_parts.append("För mer detaljerad AI-analys, använd 'snabb' eller 'smart' profil med externa AI-providers.")
            
            # Approximera tokens använda (anta ~4 tecken per token)
            full_response = "\n".join(response_parts)
            estimated_tokens = len(full_response) // 4
            
            return {
                "svar": full_response,
                "modell": model,  # Använd modell-parametern
                "provider": "lokal",
                "typ": "rule_based",
                "tokens_used": estimated_tokens
            }
        except Exception as e:
            logger.error(f"Lokal analys fel: {e}", exc_info=True)
            raise
    
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str = "lokal",
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """
        Lokal streaming - yield:ar hela svaret
        
        Args:
            query: Användarens fråga
            context: Kontext från datakällor
            model: AI-modell att använda
            temperature: Kreativitetsnivå
            max_tokens: Max antal tokens
            
        Yields:
            Chunks av svaret
        """
        try:
            result = await self.analyze(query, context, model, temperature, max_tokens, stream=True)
            yield result["svar"]
        except Exception as e:
            logger.error(f"Lokal streaming fel: {e}", exc_info=True)
            raise
