"""
IRIS v6.0 - xAI Grok Provider
Fallback provider för smart profil
"""

import logging
from typing import Dict, Any, AsyncIterator
import aiohttp
from .base import BaseAIProvider

logger = logging.getLogger(__name__)

class XAIProvider(BaseAIProvider):
    """
    xAI Grok Provider
    Används för smart profil och som fallback
    """
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        logger.info("🧠 XAIProvider initialiserad")
    
    def get_provider_name(self) -> str:
        return "xai"
    
    async def analyze(
        self,
        query: str,
        context: str,
        model: str = "grok-beta",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Analysera med xAI Grok
        
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
            if model is None:
                model = "grok-beta"
            
            # Säkerställ giltiga värden
            temperature = max(0.0, min(1.0, temperature))
            max_tokens = max(1, min(4096, max_tokens))
            
            from src.utils.error_handling import retry_with_backoff
            
            @retry_with_backoff(max_retries=2)
            async def make_api_call():
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": self._build_system_prompt()
                            },
                            {
                                "role": "user",
                                "content": self._build_user_prompt(query, context)
                            }
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Säker kontroll av respons-struktur
                            if not data.get("choices") or len(data["choices"]) == 0:
                                raise Exception("xAI API returnerade ingen giltig respons")
                            
                            choice = data["choices"][0]
                            if not choice.get("message") or "content" not in choice["message"]:
                                raise Exception("xAI API returnerade ingen giltig meddelande")
                            
                            content = choice["message"]["content"]
                            
                            return {
                                "svar": content,
                                "modell": model,
                                "provider": "xai",
                                "typ": "ai_analysis",
                                "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                            }
                        else:
                            error_text = await response.text()
                            raise Exception(f"xAI API fel: {response.status} - {error_text}")
            
            return await make_api_call()
            
        except Exception as e:
            logger.error(f"xAI API fel: {e}", exc_info=True)
            raise
    
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str = "grok-beta",
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> AsyncIterator[str]:
        """
        xAI stödjer inte streaming än
        Yield:ar hela svaret som en chunk
        
        Args:
            query: Användarens fråga
            context: Kontext från datakällor
            model: AI-modell att använda
            temperature: Kreativitetsnivå
            max_tokens: Max antal tokens
            
        Yields:
            Chunks av svaret
        """
        # Input validation
        if query is None:
            query = ""
        if context is None:
            context = ""
        if model is None:
            model = "grok-beta"
        
        # Säkerställ giltiga värden
        temperature = max(0.0, min(1.0, temperature))
        max_tokens = max(1, min(4096, max_tokens))
        
        logger.warning("xAI streaming inte tillgängligt, använder non-streaming")
        result = await self.analyze(query, context, model, temperature, max_tokens, stream=False)
        yield result["svar"]
