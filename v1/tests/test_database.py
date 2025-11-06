"""
IRIS v6.0 - Database Tests
Testar databasoperationer och GDPR-funktionalitet
"""

import pytest
from datetime import datetime

@pytest.mark.asyncio
class TestDatabase:
    """Test database operations"""
    
    async def test_database_initialization(self, test_db):
        """Test databas-initialisering"""
        assert test_db.engine is not None
        assert test_db.session_maker is not None
    
    async def test_health_check(self, test_db):
        """Test databas hälsokontroll"""
        is_healthy = await test_db.health_check()
        assert is_healthy is True
    
    async def test_consent_operations(self, test_db):
        """Test GDPR-samtycke operationer"""
        user_id = "test_user_123"
        
        # Uppdatera samtycke
        await test_db.update_consent(
            user_id=user_id,
            analytics=True,
            data_processing=True
        )
        
        # Hämta samtycke
        consent = await test_db.get_consent(user_id)
        assert consent is not None
        assert consent["analytics"] is True
        assert consent["data_processing"] is True
        assert "given_at" in consent
    
    async def test_query_logging(self, test_db):
        """Test loggning av frågor"""
        await test_db.log_query(
            user_id="test_user",
            query_hash="abc123",
            profile="smart",
            sources=["scb", "omx"],
            processing_time=1500,
            success=True,
            gdpr_consent=True
        )
        
        # Verifiera att loggning lyckades (ingen exception)
        assert True
    
    async def test_delete_user_data(self, test_db):
        """Test radering av användardata (GDPR)"""
        user_id = "delete_test_user"
        
        # Skapa data
        await test_db.update_consent(
            user_id=user_id,
            analytics=True,
            data_processing=True
        )
        
        await test_db.log_query(
            user_id=user_id,
            query_hash="test_hash",
            profile="smart",
            sources=["scb"],
            processing_time=1000,
            success=True,
            gdpr_consent=True
        )
        
        # Radera data
        await test_db.delete_user_data(user_id)
        
        # Verifiera radering
        consent = await test_db.get_consent(user_id)
        assert consent is None
    
    async def test_cleanup_old_data(self, test_db):
        """Test rensning av gammal data"""
        # Denna test verifierar att cleanup körs utan fel
        await test_db.cleanup_old_data(days=30)
        assert True
