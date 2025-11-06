"""
IRIS v6.0 - Model Configuration Manager
Centraliserad hantering av AI-modellkonfigurationer
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Konfiguration för en AI-modell"""
    namn: str
    provider: str
    model_id: str
    beskrivning: str
    max_tokens: int
    default_temperature: float
    supports_streaming: bool
    hastighet: str
    kostnad: str
    rekommenderad_för: List[str]
    privat: bool = False
    supports_vision: bool = False


class ModelConfigManager:
    """
    Manager för AI-modellkonfigurationer
    Laddar och hanterar modeller från YAML-konfiguration
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialisera ModelConfigManager
        
        Args:
            config_path: Sökväg till models.yaml, None för default
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "../../config/models.yaml"
        )
        self.models: Dict[str, ModelConfig] = {}
        self.profil_modeller: Dict[str, Dict[str, Any]] = {}
        self.användningsfall: Dict[str, Dict[str, Any]] = {}
        
        self._load_configuration()
        logger.info(f"✅ Laddade {len(self.models)} modellkonfigurationer")
    
    def _load_configuration(self):
        """Ladda modellkonfigurationer från YAML-fil"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                    # Ladda modeller
                    for model_key, model_data in config.get('ai_models', {}).items():
                        self.models[model_key] = ModelConfig(
                            namn=model_data.get('namn', model_key),
                            provider=model_data.get('provider', 'unknown'),
                            model_id=model_data.get('model_id', model_key),
                            beskrivning=model_data.get('beskrivning', ''),
                            max_tokens=model_data.get('max_tokens', 2048),
                            default_temperature=model_data.get('default_temperature', 0.7),
                            supports_streaming=model_data.get('supports_streaming', False),
                            hastighet=model_data.get('hastighet', 'medel'),
                            kostnad=model_data.get('kostnad', 'medel'),
                            rekommenderad_för=model_data.get('rekommenderad_för', []),
                            privat=model_data.get('privat', False),
                            supports_vision=model_data.get('supports_vision', False)
                        )
                    
                    # Ladda profil-mappningar
                    self.profil_modeller = config.get('profil_modeller', {})
                    
                    # Ladda användningsfall
                    self.användningsfall = config.get('användningsfall', {})
            else:
                logger.warning(f"⚠️ Models config inte funnen: {self.config_path}, använder defaults")
                self._load_default_models()
                
        except Exception as e:
            logger.error(f"❌ Kunde inte ladda models config: {e}", exc_info=True)
            self._load_default_models()
    
    def _load_default_models(self):
        """Ladda default modellkonfigurationer"""
        self.models = {
            "kimi-k2": ModelConfig(
                namn="Kimi K2 Instruct",
                provider="groq",
                model_id="moonshotai/kimi-k2-instruct-0905",
                beskrivning="Kimi K2 - Snabb och kraftfull modell",
                max_tokens=8192,
                default_temperature=0.6,
                supports_streaming=True,
                hastighet="mycket snabb",
                kostnad="låg",
                rekommenderad_för=["snabba svar", "svenska frågor"]
            ),
            "lokal": ModelConfig(
                namn="Lokal Regelbaserad",
                provider="lokal",
                model_id="lokal",
                beskrivning="Regelbaserad lokal AI",
                max_tokens=1000,
                default_temperature=0.0,
                supports_streaming=True,
                hastighet="extremt snabb",
                kostnad="gratis",
                rekommenderad_för=["privat", "GDPR"],
                privat=True
            )
        }
        
        self.profil_modeller = {
            "snabb": {"primär": "kimi-k2", "alternativ": [], "fallback": "lokal"},
            "smart": {"primär": "kimi-k2", "alternativ": [], "fallback": "lokal"},
            "privat": {"primär": "lokal", "alternativ": [], "fallback": "lokal"}
        }
    
    def get_model(self, model_key: str) -> Optional[ModelConfig]:
        """
        Hämta modellkonfiguration
        
        Args:
            model_key: Modellens nyckel (t.ex. "kimi-k2")
            
        Returns:
            ModelConfig eller None om modellen inte finns
        """
        return self.models.get(model_key)
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        """
        Hämta modellkonfiguration via model_id
        
        Args:
            model_id: Modellens ID (t.ex. "moonshotai/kimi-k2-instruct-0905")
            
        Returns:
            ModelConfig eller None om modellen inte finns
        """
        for model_config in self.models.values():
            if model_config.model_id == model_id:
                return model_config
        return None
    
    def get_models_by_provider(self, provider: str) -> List[ModelConfig]:
        """
        Hämta alla modeller för en provider
        
        Args:
            provider: Provider-namn (groq, xai, lokal)
            
        Returns:
            Lista med ModelConfig
        """
        return [
            model for model in self.models.values()
            if model.provider.lower() == provider.lower()
        ]
    
    def get_model_for_profile(self, profile_name: str) -> Optional[str]:
        """
        Hämta primär modell för en profil
        
        Args:
            profile_name: Profil-namn (snabb, smart, privat)
            
        Returns:
            Modell-nyckel eller None
        """
        profile_config = self.profil_modeller.get(profile_name, {})
        return profile_config.get('primär')
    
    def get_fallback_models(self, profile_name: str) -> List[str]:
        """
        Hämta fallback-modeller för en profil
        
        Args:
            profile_name: Profil-namn
            
        Returns:
            Lista med modell-nycklar
        """
        profile_config = self.profil_modeller.get(profile_name, {})
        alternativ = profile_config.get('alternativ', [])
        fallback = profile_config.get('fallback')
        
        models = alternativ.copy()
        if fallback and fallback not in models:
            models.append(fallback)
        
        return models
    
    def get_recommended_models(self, användningsfall: str) -> List[str]:
        """
        Hämta rekommenderade modeller för ett användningsfall
        
        Args:
            användningsfall: Användningsfall-nyckel
            
        Returns:
            Lista med modell-nycklar
        """
        case_config = self.användningsfall.get(användningsfall, {})
        return case_config.get('rekommenderade_modeller', [])
    
    def list_all_models(self) -> Dict[str, str]:
        """
        Lista alla tillgängliga modeller
        
        Returns:
            Dict med modell-nyckel -> beskrivning
        """
        return {
            key: config.beskrivning
            for key, config in self.models.items()
        }
    
    def get_model_info(self, model_key: str) -> Dict[str, Any]:
        """
        Hämta detaljerad information om en modell
        
        Args:
            model_key: Modell-nyckel
            
        Returns:
            Dict med modellinformation
        """
        model = self.get_model(model_key)
        if not model:
            return {}
        
        return {
            "namn": model.namn,
            "provider": model.provider,
            "model_id": model.model_id,
            "beskrivning": model.beskrivning,
            "max_tokens": model.max_tokens,
            "default_temperature": model.default_temperature,
            "supports_streaming": model.supports_streaming,
            "supports_vision": model.supports_vision,
            "hastighet": model.hastighet,
            "kostnad": model.kostnad,
            "rekommenderad_för": model.rekommenderad_för,
            "privat": model.privat
        }
    
    def filter_models(
        self,
        provider: Optional[str] = None,
        streaming: Optional[bool] = None,
        privat: Optional[bool] = None,
        max_kostnad: Optional[str] = None
    ) -> List[str]:
        """
        Filtrera modeller baserat på kriterier
        
        Args:
            provider: Filtrera på provider
            streaming: Filtrera på streaming-support
            privat: Filtrera på privat-flagga
            max_kostnad: Max kostnad (gratis, låg, medel, hög)
            
        Returns:
            Lista med modell-nycklar
        """
        kostnad_ordning = {"gratis": 0, "låg": 1, "medel": 2, "hög": 3}
        max_kostnad_värde = kostnad_ordning.get(max_kostnad, 999) if max_kostnad else 999
        
        filtered = []
        for key, model in self.models.items():
            # Kontrollera provider
            if provider and model.provider.lower() != provider.lower():
                continue
            
            # Kontrollera streaming
            if streaming is not None and model.supports_streaming != streaming:
                continue
            
            # Kontrollera privat
            if privat is not None and model.privat != privat:
                continue
            
            # Kontrollera kostnad
            model_kostnad_värde = kostnad_ordning.get(model.kostnad, 999)
            if model_kostnad_värde > max_kostnad_värde:
                continue
            
            filtered.append(key)
        
        return filtered


@lru_cache()
def get_model_config_manager() -> ModelConfigManager:
    """
    Cached instance av ModelConfigManager
    
    Returns:
        ModelConfigManager singleton
    """
    return ModelConfigManager()
