"""
IRIS v6.0 - AI Analyzer
xAI Grok integration för intelligent analys
"""

import logging
from typing import Dict, Any, Optional
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    AI-analys med xAI Grok och fallback till lokal modell
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        self.client = None
        logger.info("🧠 AIAnalyzer initialiserad")
    
    async def analyze(
        self,
        query: str,
        context_data: Dict[str, Any],
        profile: str,
        profile_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analysera fråga med AI baserat på samlad data
        """
        model = profile_config.get("ai_model", "grok-beta")
        
        logger.info(f"🤖 Analyserar med modell: {model}")
        
        # Bygg kontext från samlad data
        context = self._build_context(context_data)
        
        # Använd xAI API om tillgängligt
        if self.settings.xai_api_key and profile_config.get("externa_anrop", True):
            try:
                result = await self._analyze_with_xai(query, context, model)
                return result
            except Exception as e:
                logger.warning(f"xAI API misslyckades: {e}, använder fallback")
        
        # Fallback till enkel analys
        return self._analyze_locally(query, context)
    
    async def _analyze_with_xai(
        self,
        query: str,
        context: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Analysera med xAI Grok API
        """
        from src.utils.error_handling import retry_with_backoff
        
        @retry_with_backoff(max_retries=2)
        async def make_api_call():
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.settings.xai_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Bygg prompt på svenska
                prompt = f"""Du är IRIS, en intelligent svensk assistent.

Användarfråga: {query}

Kontext från svenska datakällor:
{context}

Ge ett komplett, informativt svar på svenska baserat på kontexten ovan."""

                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Du är IRIS, en intelligent svensk assistent som analyserar data och ger hjälpsamma svar på svenska."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500
                }
                
                async with session.post(
                    f"{self.settings.xai_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.settings.xai_timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        return {
                            "svar": content,
                            "modell": model,
                            "typ": "ai_analysis",
                            "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"xAI API fel: {response.status} - {error_text}")
        
        return await make_api_call()
    
    def _analyze_locally(self, query: str, context: str) -> Dict[str, Any]:
        """
        Enkel lokal analys utan externa API:er
        """
        logger.info("💻 Använder lokal analys")
        
        # Enkel regelbaserad analys för demonstration
        response_parts = [
            f"Baserat på din fråga '{query}' och tillgängliga svenska källor:"
        ]
        
        # Analysera kontext
        if "omx" in context.lower():
            response_parts.append("- Finansiell data från OMX Stockholm visar aktuell börsaktivitet.")
        
        if "scb" in context.lower():
            response_parts.append("- Statistik från SCB ger officiella svenska siffror.")
        
        if "smhi" in context.lower():
            response_parts.append("- Väderdata från SMHI ger prognoser för Sverige.")
        
        if "nyheter" in context.lower() or "news" in context.lower():
            response_parts.append("- Aktuella nyheter från svenska medier.")
        
        response_parts.append("\nFör mer detaljerad AI-analys, konfigurera xAI API-nyckel.")
        
        return {
            "svar": "\n".join(response_parts),
            "modell": "lokal",
            "typ": "rule_based",
            "tokens_used": 0
        }
    
    def _build_context(self, context_data: Dict[str, Any]) -> str:
        """
        Bygg kontext-sträng från samlad data
        """
        context_parts = []
        
        for source, data in context_data.items():
            if isinstance(data, dict) and not data.get("error"):
                context_parts.append(f"\n=== {source.upper()} ===")
                
                # Formatera data baserat på källa
                if source == "omx":
                    if "price" in data:
                        context_parts.append(f"OMX Index: {data['price']}")
                elif source == "scb":
                    if "summary" in data:
                        context_parts.append(data["summary"])
                elif source == "svenska_nyheter":
                    if "headlines" in data:
                        context_parts.append("Senaste nyheterna:")
                        for headline in data["headlines"][:3]:
                            context_parts.append(f"- {headline}")
                elif source == "smhi":
                    if "forecast" in data:
                        context_parts.append(f"Väder: {data['forecast']}")
                
                # Generisk data-representation
                elif "summary" in data:
                    context_parts.append(str(data["summary"]))
        
        return "\n".join(context_parts) if context_parts else "Ingen data tillgänglig från källor."
