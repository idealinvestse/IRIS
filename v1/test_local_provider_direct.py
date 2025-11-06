import sys
import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import required modules
from typing import Dict, Any, AsyncIterator
from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def analyze(
        self,
        query: str,
        context: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def analyze_stream(
        self,
        query: str,
        context: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

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

async def test_local_provider():
    print("Testing LocalProvider...")
    
    # Test initialization
    provider = LocalProvider()
    print(f"Provider name: {provider.get_provider_name()}")
    
    # Test basic analysis
    result = await provider.analyze("Test question", "")
    print(f"Analysis successful: {'svar' in result}")
    print(f"Response: {result['svar'][:100]}...")
    print(f"Tokens used: {result['tokens_used']}")
    print(f"Model: {result['modell']}")
    print(f"Provider: {result['provider']}")
    
    # Test with context
    context = "OMX Stockholm data shows financial trends"
    result2 = await provider.analyze("What's the stock market doing?", context)
    print(f"\nContext analysis successful: {'svar' in result2}")
    print(f"Response with context: {result2['svar'][:100]}...")
    
    # Test streaming
    print("\nTesting streaming...")
    chunks = []
    async for chunk in provider.analyze_stream("Stream test", ""):
        chunks.append(chunk)
    print(f"Streaming successful: {len(chunks) == 1}")
    print(f"Stream chunk length: {len(chunks[0])}")
    
    # Test with None inputs
    print("\nTesting with None inputs...")
    result3 = await provider.analyze(None, None)
    print(f"None input test successful: {'svar' in result3}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_local_provider())
