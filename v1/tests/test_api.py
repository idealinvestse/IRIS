"""
IRIS v6.0 - API Tests
Testar FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "meddelande" in data
        assert "version" in data
        assert data["version"] == "6.0.0"
    
    def test_health_endpoint(self):
        """Test hälso-endpoint"""
        response = client.get("/hälsa")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "tjänster" in data
        assert "system_info" in data
    
    def test_profiles_endpoint(self):
        """Test profiler-endpoint"""
        response = client.get("/profiler")
        assert response.status_code == 200
        data = response.json()
        assert "tillgängliga_profiler" in data
        assert "snabb" in data["tillgängliga_profiler"]
        assert "smart" in data["tillgängliga_profiler"]
        assert "privat" in data["tillgängliga_profiler"]
    
    def test_gdpr_info_endpoint(self):
        """Test GDPR info-endpoint"""
        response = client.get("/gdpr/info")
        assert response.status_code == 200
        data = response.json()
        assert "gdpr_aktiverat" in data
        assert "användarrättigheter" in data
    
    @pytest.mark.asyncio
    async def test_analyze_endpoint_simple_query(self):
        """Test analysera-endpoint med enkel fråga"""
        response = client.post(
            "/analysera",
            json={
                "query": "Vad är OMX-kursen?",
                "profil": "snabb",
                "användar_id": "anonym"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "framgång" in data
        assert "profil_använd" in data
        assert "resultat" in data
        assert "bearbetningstid" in data
    
    @pytest.mark.asyncio
    async def test_analyze_endpoint_complex_query(self):
        """Test analysera-endpoint med komplex fråga"""
        response = client.post(
            "/analysera",
            json={
                "query": "Analysera svenska ekonomins utveckling",
                "profil": "smart",
                "användar_id": "anonym"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "resultat" in data
    
    def test_analyze_endpoint_validation(self):
        """Test validering av analysera-endpoint"""
        # För kort fråga
        response = client.post(
            "/analysera",
            json={
                "query": "ab",  # För kort
                "profil": "snabb"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_endpoint_invalid_profile(self):
        """Test ogiltig profil"""
        response = client.post(
            "/analysera",
            json={
                "query": "Test fråga här",
                "profil": "invalid_profile"
            }
        )
        
        # Ska fortfarande fungera, använder fallback
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_gdpr_consent_endpoint(self):
        """Test GDPR samtyckes-endpoint"""
        response = client.post(
            "/gdpr/samtycke",
            params={"user_id": "test_user_consent"},
            json={
                "analytics": True,
                "data_processing": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["framgång"] is True

class TestAPIErrorHandling:
    """Test API error handling"""
    
    def test_404_handling(self):
        """Test 404 hantering"""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test felaktig HTTP-metod"""
        response = client.get("/analysera")  # Ska vara POST
        assert response.status_code == 405
