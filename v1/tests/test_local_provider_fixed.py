"""
IRIS v6.0 - Test för fixad LocalProvider
Enkel test för att verifiera att fixarna fungerar
"""

import pytest
from src.services.ai_providers.local_provider import LocalProvider


class TestLocalProviderFixed:
    """Test fixad LocalProvider"""
    
    def test_local_provider_initialization(self):
        """Test lokal provider initialisering"""
        provider = LocalProvider()
        assert provider.get_provider_name() == "lokal"
    
    @pytest.mark.asyncio
    async def test_local_analyze_basic(self):
        """Test lokal analys grundläggande"""
        provider = LocalProvider()
        
        result = await provider.analyze(
            query="Test fråga",
            context="",
            model="lokal"
        )
        
        assert "svar" in result
        assert result["provider"] == "lokal"
        assert result["modell"] == "lokal"
        assert result["typ"] == "rule_based"
        assert isinstance(result["tokens_used"], int)
        assert result["tokens_used"] >= 0
    
    @pytest.mark.asyncio
    async def test_local_analyze_with_none_inputs(self):
        """Test lokal analys med None inputs"""
        provider = LocalProvider()
        
        # Should not raise an exception
        result = await provider.analyze(
            query=None,
            context=None,
            model="lokal"
        )
        
        assert "svar" in result
        assert len(result["svar"]) > 0
    
    @pytest.mark.asyncio
    async def test_local_streaming(self):
        """Test lokal streaming"""
        provider = LocalProvider()
        
        chunks = []
        async for chunk in provider.analyze_stream("Test", ""):
            chunks.append(chunk)
        
        assert len(chunks) == 1  # Lokal yield:ar hela svaret som en chunk
        assert len(chunks[0]) > 0
    
    @pytest.mark.asyncio
    async def test_local_analyze_with_model_parameter(self):
        """Test att modell-parametern används korrekt"""
        provider = LocalProvider()
        
        result = await provider.analyze(
            query="Test",
            context="",
            model="test-model"
        )
        
        assert result["modell"] == "test-model"
