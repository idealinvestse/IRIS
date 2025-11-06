"""
IRIS v6.0 - Configuration Tests
Testar konfigurationshantering och inställningar
"""

import pytest
from src.core.config import get_settings, Settings

class TestConfiguration:
    """Test configuration management"""
    
    def test_settings_singleton(self):
        """Test att settings är singleton"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_default_profiles(self, test_settings):
        """Test att default-profiler laddas"""
        assert "snabb" in test_settings.profiles
        assert "smart" in test_settings.profiles
        assert "privat" in test_settings.profiles
    
    def test_default_swedish_sources(self, test_settings):
        """Test att svenska källor laddas"""
        assert "scb" in test_settings.swedish_sources
        assert "omx" in test_settings.swedish_sources
        assert "smhi" in test_settings.swedish_sources
        assert "svenska_nyheter" in test_settings.swedish_sources
    
    def test_profile_config_retrieval(self, test_settings):
        """Test hämtning av profil-konfiguration"""
        snabb_config = test_settings.get_profile_config("snabb")
        assert snabb_config is not None
        assert "beskrivning" in snabb_config
        assert "ai_model" in snabb_config
    
    def test_source_config_retrieval(self, test_settings):
        """Test hämtning av käll-konfiguration"""
        scb_config = test_settings.get_source_config("scb")
        assert scb_config is not None
        assert scb_config["typ"] == "statistik"
        assert scb_config["gdpr_kompatibel"] is True
    
    def test_sources_for_profile(self, test_settings):
        """Test hämtning av källor för en profil"""
        sources = test_settings.get_sources_for_profile("smart")
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert len(sources) <= 5  # smart profil max 5 källor
    
    def test_private_profile_no_external_apis(self, test_settings):
        """Test att privat profil inte använder externa API:er"""
        sources = test_settings.get_sources_for_profile("privat")
        for source in sources:
            source_config = test_settings.get_source_config(source)
            # Privat profil ska inte använda källor som kräver API-nycklar
            if source_config.get("kräver_api_nyckel"):
                pytest.fail(f"Privat profil använder källa {source} som kräver API-nyckel")
    
    def test_cache_ttl_retrieval(self, test_settings):
        """Test hämtning av cache TTL"""
        ttl = test_settings.get_cache_ttl("scb")
        assert isinstance(ttl, int)
        assert ttl > 0
    
    def test_is_production(self, test_settings):
        """Test production-kontroll"""
        assert not test_settings.is_production()  # Vi är i test-miljö
    
    def test_gdpr_enabled_by_default(self, test_settings):
        """Test att GDPR är aktiverat som standard"""
        assert test_settings.gdpr_enabled is True
