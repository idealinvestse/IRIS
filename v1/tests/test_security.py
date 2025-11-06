"""
IRIS v6.0 - Security Tests
Testar säkerhet och GDPR-funktioner
"""

import pytest
from src.core.security import SecurityManager

class TestSecurity:
    """Test security and GDPR functions"""
    
    def test_security_manager_initialization(self):
        """Test SecurityManager initialisering"""
        security = SecurityManager()
        assert security is not None
        assert security.settings is not None
    
    def test_hash_query(self):
        """Test query hashing"""
        security = SecurityManager()
        query = "Test fråga för hashing"
        hash1 = security.hash_query(query)
        hash2 = security.hash_query(query)
        
        assert hash1 == hash2  # Samma query ska ge samma hash
        assert len(hash1) == 64  # SHA-256 hash är 64 tecken
    
    def test_anonymize_user_id(self):
        """Test anonymisering av användar-ID"""
        security = SecurityManager()
        
        user_id = "user@example.com"
        anon_id = security.anonymize_user_id(user_id)
        
        assert anon_id != user_id
        assert len(anon_id) == 16  # Vi använder 16 tecken
        
        # Anonym användare ska förbli anonym
        assert security.anonymize_user_id("anonym") == "anonym"
    
    def test_injection_detection(self):
        """Test detektion av injection-attacker"""
        security = SecurityManager()
        
        # Säker input
        assert not security._contains_injection_patterns("Normal fråga om väder")
        
        # Osäker input
        assert security._contains_injection_patterns("<script>alert('xss')</script>")
        assert security._contains_injection_patterns("SELECT * FROM users")
        assert security._contains_injection_patterns("DROP TABLE users")
    
    def test_sanitize_output(self):
        """Test sanering av output"""
        security = SecurityManager()
        
        data = {
            "result": "Bra resultat",
            "api_key": "xai-secretkey123",
            "nested": {
                "bearer": "Bearer secret_token"
            }
        }
        
        sanitized = security.sanitize_output(data)
        
        # API-nycklar ska vara maskerade
        assert "xai-secretkey123" not in str(sanitized)
        assert "***API_KEY***" in str(sanitized)
    
    def test_api_key_validation(self):
        """Test validering av API-nycklar"""
        security = SecurityManager()
        
        # Giltig xAI nyckel
        valid_xai = "xai-" + "a" * 40
        assert security.validate_api_key(valid_xai, "xai")
        
        # Ogiltig xAI nyckel
        assert not security.validate_api_key("invalid", "xai")
    
    def test_get_gdpr_info(self):
        """Test hämtning av GDPR-information"""
        security = SecurityManager()
        gdpr_info = security.get_gdpr_info()
        
        assert "gdpr_aktiverat" in gdpr_info
        assert "användarrättigheter" in gdpr_info
        assert gdpr_info["användarrättigheter"]["rätt_till_radering"] is True
    
    @pytest.mark.asyncio
    async def test_verify_gdpr_consent_anonymous(self):
        """Test GDPR-samtycke för anonym användare"""
        security = SecurityManager()
        
        # Anonyma användare behöver inte samtycke
        consent = await security.verify_gdpr_consent("anonym")
        assert consent is True
