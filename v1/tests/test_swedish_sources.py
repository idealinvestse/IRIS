"""
IRIS v6.0 - Swedish Sources Tests
Testar svenska datakällor
"""

import pytest
from src.services.swedish_sources import SwedishSources

@pytest.mark.asyncio
class TestSwedishSources:
    """Test Swedish data sources"""
    
    async def test_sources_initialization(self):
        """Test initialisering av källor"""
        sources = SwedishSources()
        assert sources is not None
        assert sources.settings is not None
    
    async def test_scb_data_retrieval(self):
        """Test SCB datahämtning"""
        sources = SwedishSources()
        query = "befolkning sverige"
        
        data = await sources.get_scb_data(query)
        
        assert data is not None
        assert data["source"] == "SCB"
        assert "available" in data
        assert data["available"] is True
        assert "data" in data or "summary" in data
    
    async def test_omx_data_retrieval(self):
        """Test OMX datahämtning"""
        sources = SwedishSources()
        
        data = await sources.get_omx_data()
        
        assert data is not None
        assert "OMX" in data["source"]
        assert "price" in data
        assert "currency" in data
    
    async def test_news_data_retrieval(self):
        """Test nyhetshämtning"""
        sources = SwedishSources()
        query = "sverige ekonomi"
        
        data = await sources.get_swedish_news(query)
        
        assert data is not None
        assert "Svenska Nyheter" in data["source"]
        assert "headlines" in data
        assert isinstance(data["headlines"], list)
    
    async def test_smhi_data_retrieval(self):
        """Test SMHI väderdata"""
        sources = SwedishSources()
        query = "väder stockholm"
        
        data = await sources.get_smhi_data(query)
        
        assert data is not None
        assert data["source"] == "SMHI"
        assert "forecast" in data or "temperature" in data
        assert "available" in data
    
    async def test_error_handling(self):
        """Test felhantering i källor"""
        sources = SwedishSources()
        
        # Alla källor ska returnera data med error-hantering
        # Även om API:er fallerar ska vi få strukturerad data tillbaka
        data = await sources.get_scb_data("test")
        assert "source" in data or "error" in data
