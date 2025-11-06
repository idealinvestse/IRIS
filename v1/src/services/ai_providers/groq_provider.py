"""
IRIS v6.0 - Groq Cloud Provider
Kimi K2 integration med streaming-support
"""

import logging
from typing import Dict, Any, AsyncIterator
from groq import AsyncGroq
from .base import BaseAIProvider

logger = logging.getLogger(__name__)

class GroqProvider(BaseAIProvider):
    """
    Groq Cloud AI Provider med Kimi K2
    Optimerad för snabba svar med streaming-support
    """
    
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.client = AsyncGroq(
            api_key=api_key,
            timeout=timeout
        )
        logger.info("🚀 GroqProvider initialiserad med Kimi K2")
    
    def get_provider_name(self) -> str:
        return "groq"
    
    async def analyze(
        self,
        query: str,
        context: str,
        model: str = "moonshotai/kimi-k2-instruct-0905",
        temperature: float = 0.6,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Analysera med Groq Kimi K2
        
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
                model = "moonshotai/kimi-k2-instruct-0905"
            
            # Säkerställ giltiga värden
            temperature = max(0.0, min(1.0, temperature))
            max_tokens = max(1, min(8192, max_tokens))
            
            # Add retry with backoff for consistency with other providers
            from src.utils.error_handling import retry_with_backoff
            
            @retry_with_backoff(max_retries=2)
            async def make_api_call():
                if stream:
                    # För streaming, samla allt innehåll
                    full_content = ""
                    async for chunk in self.analyze_stream(
                        query, context, model, temperature, max_tokens
                    ):
                        full_content += chunk
                    
                    # För streaming, försök att få faktisk token count från API
                    # Om inte tillgänglig, använd bättre approximation
                    estimated_tokens = len(full_content) // 4  # Bättre approximation: ~4 tecken per token
                    
                    return {
                        "svar": full_content,
                        "modell": model,
                        "provider": "groq",
                        "typ": "ai_analysis_streaming",
                        "tokens_used": estimated_tokens
                    }
                else:
                    # Non-streaming
                    completion = await self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": self._build_system_prompt()
                            },
                            {
                                "role": "user",
                                "content": self._build_user_prompt(query, context)
                            }
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=1,
                        stream=False,
                        stop=None
                    )
                    
                    content = completion.choices[0].message.content
                    
                    return {
                        "svar": content,
                        "modell": model,
                        "provider": "groq",
                        "typ": "ai_analysis",
                        "tokens_used": completion.usage.total_tokens if hasattr(completion, 'usage') and completion.usage and hasattr(completion.usage, 'total_tokens') else 0
                    }
            
            return await make_api_call()
        except Exception as e:
            logger.error(f"Groq API fel: {e}", exc_info=True)
            raise
    
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str = "moonshotai/kimi-k2-instruct-0905",
        temperature: float = 0.6,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """
        Streaming-analys med Groq Kimi K2
        Yield:ar chunks av svaret i real-time
        
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
            # Input validation
            if query is None:
                query = ""
            if context is None:
                context = ""
            if model is None:
                model = "moonshotai/kimi-k2-instruct-0905"
            
            # Säkerställ giltiga värden
            temperature = max(0.0, min(1.0, temperature))
            max_tokens = max(1, min(8192, max_tokens))
            logger.info(f"🌊 Startar Groq streaming med {model}")
            
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": self._build_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": self._build_user_prompt(query, context)
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=True,
                stop=None
            )
            
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and hasattr(delta, 'content') and delta.content is not None:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"Groq streaming fel: {e}", exc_info=True)
            raise
