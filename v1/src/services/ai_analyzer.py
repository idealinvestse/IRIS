"""
IRIS v6.0 - AI Analyzer (Uppdaterad med Multi-Provider Support)
Stödjer Groq Cloud (Kimi K2), xAI Grok och lokal AI
"""

import logging
from typing import Dict, Any, Optional
from src.services.ai_providers.factory import AIProviderFactory
from src.services.ai_providers.base import BaseAIProvider

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    AI-analys med multi-provider support
    Automatisk fallback: Groq → xAI → Lokal
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        self.provider_cache: Dict[str, Optional[BaseAIProvider]] = {}
        logger.info("🧠 AIAnalyzer initialiserad (multi-provider mode)")
    
    async def analyze(
        self,
        query: str,
        context_data: Dict[str, Any],
        profile: str,
        profile_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analysera fråga med vald AI-provider
        
        Args:
            query: Användarfråga
            context_data: Data från svenska källor
            profile: Profil-namn (snabb, smart, privat)
            profile_config: Profil-konfiguration
            
        Returns:
            Dict med AI-analys
        """
        # Hämta provider-specifik konfiguration
        provider_name = profile_config.get("ai_provider", "lokal")
        model = profile_config.get("ai_model", "lokal")
        temperature = profile_config.get("temperature", 0.7)
        max_tokens = profile_config.get("max_tokens", 2048)
        streaming = profile_config.get("streaming", False)
        
        logger.info(f"🤖 Analyserar med provider: {provider_name}, modell: {model}, streaming: {streaming}")
        
        # Hämta eller skapa provider
        provider = self._get_provider(provider_name)
        
        if not provider:
            logger.warning(f"⚠️ Provider {provider_name} inte tillgänglig, försöker fallback")
            provider = self._get_fallback_provider(provider_name)
        
        # Bygg kontext från datakällor
        context = self._build_context(context_data)
        
        try:
            # Analysera med vald provider
            result = await provider.analyze(
                query=query,
                context=context,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=streaming
            )
            
            logger.info(f"✅ Analys slutförd med {provider.get_provider_name()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Provider {provider_name} misslyckades: {e}", exc_info=True)
            
            # Försök fallback
            return await self._try_fallback_providers(
                query, context, provider_name, model, temperature, max_tokens
            )
    
    def _get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """
        Hämta eller skapa provider (cached)
        
        Args:
            provider_name: Namnet på providern
            
        Returns:
            Provider instance eller None
        """
        if provider_name not in self.provider_cache:
            self.provider_cache[provider_name] = AIProviderFactory.create_provider(
                provider_name, self.settings
            )
        
        return self.provider_cache[provider_name]
    
    def _get_fallback_provider(self, failed_provider: str) -> BaseAIProvider:
        """
        Hämta fallback-provider när primär provider misslyckas
        
        Fallback-ordning: groq → xai → lokal
        
        Args:
            failed_provider: Namnet på providern som misslyckades
            
        Returns:
            Fallback provider (lokal som sista utväg)
        """
        fallback_order = ["groq", "xai", "lokal"]
        
        # Ta bort den som misslyckades
        if failed_provider in fallback_order:
            fallback_order.remove(failed_provider)
        
        # Försök providers i ordning
        for provider_name in fallback_order:
            provider = self._get_provider(provider_name)
            if provider:
                logger.info(f"🔄 Använder fallback provider: {provider_name}")
                return provider
        
        # Lokal är alltid tillgänglig som sista utväg
        logger.warning("⚠️ Använder lokal provider som sista fallback")
        local_provider = self._get_provider("lokal")
        if not local_provider:
            # Om till och med lokal misslyckas, skapa en ny instans
            from src.services.ai_providers.factory import AIProviderFactory
            local_provider = AIProviderFactory.create_provider("lokal", self.settings)
            if local_provider:
                self.provider_cache["lokal"] = local_provider
        return local_provider
    
    async def _try_fallback_providers(
        self,
        query: str,
        context: str,
        failed_provider: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Försök med fallback-providers
        """
        fallback_order = ["xai", "lokal"] if failed_provider == "groq" else ["lokal"]
        
        for fallback_name in fallback_order:
            try:
                logger.info(f"🔄 Försöker fallback: {fallback_name}")
                fallback_provider = self._get_provider(fallback_name)
                
                if fallback_provider:
                    # Använd justerad temperatur för fallback
                    # Minska något för mer stabila svar i fallback
                    adjusted_temperature = max(0.1, temperature * 0.8) if temperature > 0 else 0.5
                    
                    result = await fallback_provider.analyze(
                        query=query,
                        context=context,
                        model="lokal" if fallback_name == "lokal" else model,
                        temperature=adjusted_temperature,
                        max_tokens=max_tokens,
                        stream=False
                    )
                    
                    logger.info(f"✅ Fallback {fallback_name} lyckades")
                    return result
                    
            except Exception as fallback_error:
                logger.error(f"❌ Fallback {fallback_name} misslyckades: {fallback_error}")
                continue
        
        # Om allt misslyckas, returnera fel-meddelande
        return self._error_response(query, Exception("Alla AI-providers misslyckades"))
    
    def _build_context(self, context_data: Dict[str, Any]) -> str:
        """
        Bygg kontext-sträng från samlad data
        
        Args:
            context_data: Data från svenska källor
            
        Returns:
            Formaterad kontext-sträng
        """
        context_parts = []
        
        for source, data in context_data.items():
            if isinstance(data, dict) and not data.get("error") and data.get("available"):
                context_parts.append(f"\n=== {source.upper()} ===")
                
                # Formatera data baserat på källa
                if source == "omx":
                    if "price" in data:
                        context_parts.append(f"OMX Index: {data['price']} SEK")
                        if "change" in data:
                            context_parts.append(f"Förändring: {data['change']}")
                
                elif source == "scb":
                    if "summary" in data:
                        context_parts.append(data["summary"])
                    if "data" in data:
                        for key, value in data["data"].items():
                            context_parts.append(f"{key}: {value}")
                
                elif source == "svenska_nyheter":
                    if "headlines" in data:
                        context_parts.append("Senaste nyheterna:")
                        for headline in data["headlines"][:3]:
                            context_parts.append(f"- {headline}")
                
                elif source == "smhi":
                    if "forecast" in data:
                        context_parts.append(f"Väder: {data['forecast']}")
                    if "temperature" in data:
                        context_parts.append(f"Temperatur: {data['temperature']}°C")
                
                # Generisk data-representation
                elif "summary" in data:
                    context_parts.append(str(data["summary"]))
        
        if context_parts:
            return "\n".join(context_parts)
        else:
            return "Ingen kontextdata tillgänglig från källor."
    
    def _error_response(self, query: str, error: Exception) -> Dict[str, Any]:
        """
        Generera fel-respons
        
        Args:
            query: Ursprunglig fråga
            error: Exception som orsakade felet
            
        Returns:
            Fel-respons dict
        """
        return {
            "svar": f"Kunde inte analysera frågan '{query}' på grund av tekniska problem. Alla AI-providers är tillfälligt otillgängliga.",
            "modell": "error",
            "provider": "none",
            "typ": "error",
            "tokens_used": 0,
            "error": str(error),
            "rekommendation": "Försök igen senare eller kontakta support om problemet kvarstår."
        }
    
    def get_available_providers(self) -> list:
        """
        Hämta lista över tillgängliga providers
        
        Returns:
            List av provider-namn
        """
        return AIProviderFactory.get_available_providers(self.settings)
