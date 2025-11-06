"""
IRIS v6.0 - Model Configuration Tests
Tester för modellkonfigurationssystemet
"""

import pytest
from src.core.model_config import ModelConfigManager, get_model_config_manager


class TestModelConfigManager:
    """Tester för ModelConfigManager"""
    
    def test_manager_initialization(self):
        """Test att manager initialiseras korrekt"""
        manager = ModelConfigManager()
        assert manager is not None
        assert len(manager.models) > 0
    
    def test_get_model(self):
        """Test att hämta modell via nyckel"""
        manager = get_model_config_manager()
        model = manager.get_model("kimi-k2")
        assert model is not None
        assert model.provider == "groq"
        assert model.model_id == "moonshotai/kimi-k2-instruct-0905"
    
    def test_get_model_nonexistent(self):
        """Test att hämta icke-existerande modell"""
        manager = get_model_config_manager()
        model = manager.get_model("fel-nyckel")
        assert model is None
    
    def test_get_model_by_id(self):
        """Test att hämta modell via model_id"""
        manager = get_model_config_manager()
        model = manager.get_model_by_id("moonshotai/kimi-k2-instruct-0905")
        assert model is not None
        assert model.provider == "groq"
    
    def test_get_models_by_provider(self):
        """Test att hämta modeller för en provider"""
        manager = get_model_config_manager()
        groq_models = manager.get_models_by_provider("groq")
        assert len(groq_models) > 0
        for model in groq_models:
            assert model.provider == "groq"
    
    def test_get_model_for_profile(self):
        """Test att hämta modell för profil"""
        manager = get_model_config_manager()
        primary = manager.get_model_for_profile("snabb")
        assert primary == "kimi-k2"
    
    def test_get_fallback_models(self):
        """Test att hämta fallback-modeller"""
        manager = get_model_config_manager()
        fallbacks = manager.get_fallback_models("snabb")
        assert "lokal" in fallbacks
    
    def test_get_recommended_models(self):
        """Test att hämta rekommenderade modeller"""
        manager = get_model_config_manager()
        models = manager.get_recommended_models("snabba_svar")
        assert len(models) > 0
    
    def test_list_all_models(self):
        """Test att lista alla modeller"""
        manager = get_model_config_manager()
        models = manager.list_all_models()
        assert len(models) > 0
        assert "kimi-k2" in models
        assert "lokal" in models
    
    def test_get_model_info(self):
        """Test att hämta modellinformation"""
        manager = get_model_config_manager()
        info = manager.get_model_info("kimi-k2")
        assert info is not None
        assert "namn" in info
        assert "provider" in info
        assert "model_id" in info
    
    def test_filter_models_by_provider(self):
        """Test filtrering på provider"""
        manager = get_model_config_manager()
        filtered = manager.filter_models(provider="groq")
        assert len(filtered) > 0
    
    def test_filter_models_by_streaming(self):
        """Test filtrering på streaming"""
        manager = get_model_config_manager()
        filtered = manager.filter_models(streaming=True)
        assert len(filtered) > 0
    
    def test_filter_models_by_privat(self):
        """Test filtrering på privat"""
        manager = get_model_config_manager()
        filtered = manager.filter_models(privat=True)
        assert "lokal" in filtered
    
    def test_model_config_attributes(self):
        """Test att modellkonfiguration har rätt attribut"""
        manager = get_model_config_manager()
        model = manager.get_model("kimi-k2")
        assert hasattr(model, 'namn')
        assert hasattr(model, 'provider')
        assert hasattr(model, 'model_id')
        assert hasattr(model, 'beskrivning')
        assert hasattr(model, 'max_tokens')
        assert hasattr(model, 'default_temperature')
        assert hasattr(model, 'supports_streaming')
        assert hasattr(model, 'hastighet')
        assert hasattr(model, 'kostnad')
        assert hasattr(model, 'rekommenderad_för')
    
    def test_singleton_pattern(self):
        """Test att get_model_config_manager returnerar samma instans"""
        manager1 = get_model_config_manager()
        manager2 = get_model_config_manager()
        assert manager1 is manager2


class TestSettingsIntegration:
    """Tester för integration med Settings"""
    
    def test_settings_get_model_config_manager(self):
        """Test att hämta manager från settings"""
        from src.core.config import get_settings
        settings = get_settings()
        manager = settings.get_model_config_manager()
        assert manager is not None
    
    def test_settings_get_model_for_profile(self):
        """Test att hämta modell för profil via settings"""
        from src.core.config import get_settings
        settings = get_settings()
        model_id = settings.get_model_for_profile("snabb")
        assert model_id is not None
        assert isinstance(model_id, str)
