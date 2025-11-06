"""
IRIS v6.0 - Groq Provider Tests
Testar Groq Cloud integration med Kimi K2
"""

import pytest
import os
from src.services.ai_providers.groq_provider import GroqProvider
from src.services.ai_providers.factory import AIProviderFactory

class TestGroqProvider:
    """Test Groq Cloud provider"""
    
    def test_provider_initialization(self):
        """Test Groq provider initialisering"""
        provider = GroqProvider(api_key="test-key-12345")
        assert provider.get_provider_name() == "groq"
        assert provider.api_key == "test-key-12345"
    
    def test_provider_name(self):
        """Test provider namn"""
        provider = GroqProvider(api_key="test")
        assert provider.get_provider_name() == "groq"
    
    @pytest.mark.skipif(
        not os.getenv("GROQ_API_KEY"),
        reason="GROQ_API_KEY inte satt - skippa real API test"
    )
    @pytest.mark.asyncio
    async def test_analyze_with_real_api(self):
        """Test analys med riktig Groq API"""
        provider = GroqProvider(
            api_key=os.getenv("GROQ_API_KEY"),
            timeout=30
        )
        
        result = await provider.analyze(
            query="Vad är 2+2?",
            context="",
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.6,
            max_tokens=100,
            stream=False
        )
        
        assert "svar" in result
        assert result["provider"] == "groq"
        assert result["modell"] == "moonshotai/kimi-k2-instruct-0905"
        assert len(result["svar"]) > 0
    
    @pytest.mark.skipif(
        not os.getenv("GROQ_API_KEY"),
        reason="GROQ_API_KEY inte satt"
    )
    @pytest.mark.asyncio
    async def test_streaming_with_real_api(self):
        """Test streaming med riktig API"""
        provider = GroqProvider(
            api_key=os.getenv("GROQ_API_KEY"),
            timeout=30
        )
        
        chunks = []
        async for chunk in provider.analyze_stream(
            query="Räkna till 5 på svenska",
            context="",
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.6,
            max_tokens=50
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_context(self):
        """Test analys med kontext"""
        # Mock test - behöver riktig API-nyckel för att köra
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY inte satt")
        
        provider = GroqProvider(api_key=os.getenv("GROQ_API_KEY"))
        
        context = "OMX Index: 2450 SEK. Dagens förändring: +12.3"
        result = await provider.analyze(
            query="Hur går börsen idag?",
            context=context,
            temperature=0.6
        )
        
        assert "svar" in result
        assert result["provider"] == "groq"

class TestAIProviderFactory:
    """Test AI Provider Factory"""
    
    def test_create_groq_provider(self):
        """Test skapande av Groq provider"""
        from src.core.config import Settings
        
        # Mock settings
        settings = Settings(
            groq_api_key="test-key",
            groq_timeout=10
        )
        
        provider = AIProviderFactory.create_provider("groq", settings)
        assert provider is not None
        assert provider.get_provider_name() == "groq"
    
    def test_create_provider_without_api_key(self):
        """Test att provider inte skapas utan API-nyckel"""
        from src.core.config import Settings
        
        settings = Settings()  # Ingen API-nyckel
        
        provider = AIProviderFactory.create_provider("groq", settings)
        assert provider is None
    
    def test_create_local_provider(self):
        """Test skapande av lokal provider"""
        from src.core.config import Settings
        
        settings = Settings()
        
        provider = AIProviderFactory.create_provider("lokal", settings)
        assert provider is not None
        assert provider.get_provider_name() == "lokal"
    
    def test_unknown_provider(self):
        """Test okänd provider"""
        from src.core.config import Settings
        
        settings = Settings()
        
        provider = AIProviderFactory.create_provider("unknown", settings)
        assert provider is None

@pytest.mark.asyncio
class TestMultiProviderIntegration:
    """Test integration mellan providers"""
    
    async def test_provider_fallback_order(self):
        """Test fallback-ordning"""
        from src.services.ai_analyzer_new import AIAnalyzer
        
        analyzer = AIAnalyzer()
        
        # Test fallback när groq inte är tillgänglig
        fallback = analyzer._get_fallback_provider("groq")
        assert fallback is not None
        # Ska fallback till xai eller lokal
        assert fallback.get_provider_name() in ["xai", "lokal"]
    
    async def test_context_building(self):
        """Test kontext-byggande"""
        from src.services.ai_analyzer_new import AIAnalyzer
        
        analyzer = AIAnalyzer()
        
        context_data = {
            "omx": {
                "price": 2450,
                "change": 12.3,
                "available": True
            },
            "scb": {
                "summary": "Befolkning: 10.5M",
                "available": True
            }
        }
        
        context = analyzer._build_context(context_data)
        
        assert "OMX" in context
        assert "2450" in context
        assert "SCB" in context
