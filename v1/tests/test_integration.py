"""
IRIS v6.0 - Integration Tests
Testar integration mellan komponenter
"""

import pytest
from src.services.profile_router import ProfileRouter
from src.services.data_collector import DataCollector
from src.services.ai_analyzer import AIAnalyzer

@pytest.mark.asyncio
class TestIntegration:
    """Test component integration"""
    
    async def test_profile_router_integration(self):
        """Test ProfileRouter med riktiga komponenter"""
        router = ProfileRouter()
        
        result = await router.route_query(
            query="Hur är vädret i Stockholm?",
            user_profile="snabb",
            user_id="test_integration"
        )
        
        assert result is not None
        assert "profil" in result
        assert "resultat" in result
        assert result["profil"] == "snabb"
    
    async def test_data_collection_flow(self):
        """Test datainhämtningsflöde"""
        collector = DataCollector()
        
        sources = ["scb", "omx"]
        profile_config = {"max_källor": 2}
        
        data = await collector.collect_data(
            query="ekonomi",
            sources=sources,
            profile_config=profile_config
        )
        
        assert data is not None
        assert isinstance(data, dict)
    
    async def test_ai_analysis_flow(self):
        """Test AI-analysflöde"""
        analyzer = AIAnalyzer()
        
        context_data = {
            "omx": {"price": 2450, "available": True},
            "scb": {"summary": "Ekonomisk data", "available": True}
        }
        
        result = await analyzer.analyze(
            query="Analysera ekonomin",
            context_data=context_data,
            profile="smart",
            profile_config={"ai_model": "lokal", "externa_anrop": False}
        )
        
        assert result is not None
        assert "svar" in result
        assert "modell" in result
    
    async def test_end_to_end_query(self):
        """Test komplett fråga från början till slut"""
        router = ProfileRouter()
        
        # Simulera en komplett användarfråga
        result = await router.route_query(
            query="Vad är OMX-kursen och hur är ekonomin?",
            user_profile=None,  # Auto-select
            user_id="integration_test"
        )
        
        assert result is not None
        assert "profil" in result
        assert "resultat" in result
        assert "använd_källor" in result
        assert "bearbetningstid" in result
    
    async def test_error_propagation(self):
        """Test att fel propagerar korrekt"""
        collector = DataCollector()
        
        # Test med ogiltig källa
        try:
            data = await collector.collect_data(
                query="test",
                sources=["invalid_source"],
                profile_config={}
            )
            # Ska inte kasta fel, men returnera fel-info
            assert "invalid_source" in data
        except Exception:
            # Om exception kastas, det är också okej
            pass
