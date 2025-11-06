"""
IRIS v6.0 - Base AI Provider Interface
Abstract base class för alla AI-providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator

class BaseAIProvider(ABC):
    """Abstract base class för AI-providers"""
    
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
        """
        Analysera fråga med AI
        
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
        """
        Streaming-analys med AI
        
        Args:
            query: Användarens fråga
            context: Kontext från datakällor
            model: AI-modell att använda
            temperature: Kreativitetsnivå
            max_tokens: Max antal tokens
            
        Yields:
            Chunks av svaret
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Returnera provider-namn"""
        pass
    
    def _build_system_prompt(self) -> str:
        """Standard system prompt på svenska"""
        return "Du är IRIS, en intelligent svensk assistent som analyserar data och ger hjälpsamma svar på svenska."
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Bygg user prompt med query och kontext"""
        if context and context.strip():
            return f"""Användarfråga: {query}

Kontext från svenska datakällor:
{context}

Ge ett komplett, informativt svar på svenska baserat på kontexten ovan."""
        else:
            return f"Användarfråga: {query}\n\nGe ett komplett, informativt svar på svenska."
