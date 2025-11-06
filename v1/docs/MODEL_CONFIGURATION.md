# IRIS v6.0 - Model Configuration Guide

## 📋 Översikt

IRIS v6.0 har ett kraftfullt och flexibelt system för att hantera AI-modeller. Systemet gör det enkelt att:
- Konfigurera och hantera flera AI-modeller
- Välja rätt modell för olika användningsfall
- Automatiskt använda fallback-modeller
- Filtrera modeller baserat på behov

## 🗂️ Filer

### Konfigurationsfiler
- `config/models.yaml` - Centraliserad modellkonfiguration
- `src/core/model_config.py` - Model Configuration Manager
- `src/utils/model_manager_cli.py` - CLI-verktyg för modellhantering

## 🚀 Snabbstart

### 1. Lista tillgängliga modeller

```bash
python -m src.utils.model_manager_cli list
```

### 2. Visa information om en modell

```bash
python -m src.utils.model_manager_cli info kimi-k2
```

### 3. Visa modeller för en profil

```bash
python -m src.utils.model_manager_cli profile snabb
```

### 4. Lista alla användningsfall

```bash
python -m src.utils.model_manager_cli usecases
```

## 📖 Användning i kod

### Hämta Model Config Manager

```python
from src.core.model_config import get_model_config_manager

manager = get_model_config_manager()
```

### Hämta modellkonfiguration

```python
# Hämta modell via nyckel
model = manager.get_model("kimi-k2")
print(f"Modell: {model.namn}")
print(f"Provider: {model.provider}")
print(f"Max tokens: {model.max_tokens}")

# Hämta modell via model_id
model = manager.get_model_by_id("moonshotai/kimi-k2-instruct-0905")
```

### Hämta modeller för en profil

```python
# Hämta primär modell för profil
primary_model = manager.get_model_for_profile("snabb")
print(f"Primär modell för 'snabb': {primary_model}")

# Hämta fallback-modeller
fallbacks = manager.get_fallback_models("snabb")
print(f"Fallback-modeller: {fallbacks}")
```

### Filtrera modeller

```python
# Hämta alla Groq-modeller
groq_models = manager.get_models_by_provider("groq")

# Filtrera med flera kriterier
filtered = manager.filter_models(
    provider="groq",
    streaming=True,
    max_kostnad="låg"
)
```

### Använd med Settings

```python
from src.core.config import get_settings

settings = get_settings()
manager = settings.get_model_config_manager()

# Hämta modell-ID för en profil
model_id = settings.get_model_for_profile("smart")
print(f"Modell för 'smart': {model_id}")
```

## 🛠️ Lägga till nya modeller

Redigera `config/models.yaml`:

```yaml
ai_models:
  din-nya-modell:
    namn: "Din Nya Modell"
    provider: "groq"  # eller xai, lokal
    model_id: "provider-model-id"
    beskrivning: "Beskrivning av modellen"
    max_tokens: 8192
    default_temperature: 0.7
    supports_streaming: true
    hastighet: "snabb"  # extremt snabb, mycket snabb, snabb, medel
    kostnad: "låg"  # gratis, låg, medel, hög
    rekommenderad_för:
      - "användningsfall 1"
      - "användningsfall 2"
    privat: false  # true för lokal modell
    supports_vision: false  # true för multimodal
```

## 📊 Modellattribut

### Hastighet
- **extremt snabb**: < 1 sekund
- **mycket snabb**: 1-2 sekunder
- **snabb**: 2-5 sekunder
- **medel**: 5-10 sekunder

### Kostnad
- **gratis**: Ingen kostnad (lokal)
- **låg**: Billig API-användning
- **medel**: Normal API-kostnad
- **hög**: Dyrare API-användning

## 🎯 Användningsfall

### Snabba svar
Rekommenderade modeller:
- `llama-3-8b` - Extremt snabb
- `kimi-k2` - Mycket snabb

### Komplexa analyser
Rekommenderade modeller:
- `llama-3-70b` - Kraftfull
- `grok-beta` - Avancerad
- `mixtral-8x7b` - Stor kontext

### Dokumentanalys
Rekommenderade modeller:
- `mixtral-8x7b` - 32K kontext
- `llama-3-70b` - Hög kvalitet

### Privat/Känslig data
Rekommenderade modeller:
- `lokal` - 100% privat

## 🔄 Fallback-strategi

Systemet använder automatisk fallback vid fel:

```
Profil "snabb":
  Primär → kimi-k2
  Alternativ → llama-3-8b, llama-3-70b
  Fallback → lokal

Profil "smart":
  Primär → kimi-k2
  Alternativ → llama-3-70b, grok-beta, mixtral-8x7b
  Fallback → lokal

Profil "privat":
  Primär → lokal
  Alternativ → (ingen)
  Fallback → lokal
```

## 🧪 Testning

### Test model configuration

```python
import pytest
from src.core.model_config import get_model_config_manager

def test_model_loading():
    manager = get_model_config_manager()
    assert len(manager.models) > 0

def test_get_model():
    manager = get_model_config_manager()
    model = manager.get_model("kimi-k2")
    assert model is not None
    assert model.provider == "groq"

def test_profile_mapping():
    manager = get_model_config_manager()
    primary = manager.get_model_for_profile("snabb")
    assert primary == "kimi-k2"
```

## 📝 Best Practices

1. **Använd rätt modell för rätt uppgift**
   - Snabba svar → Använd lätta modeller (llama-3-8b)
   - Komplexa analyser → Använd kraftfulla modeller (llama-3-70b)
   - Privat data → Använd lokal modell

2. **Konfigurera fallbacks**
   - Alltid ha minst en fallback-modell
   - Lokal modell som sista fallback

3. **Optimera för kostnad**
   - Använd filter för att välja kostnadseffektiva modeller
   - Testa med billigare modeller först

4. **Dokumentera användningsfall**
   - Lägg till nya användningsfall i `models.yaml`
   - Specificera rekommenderade modeller

## 🔧 Felsökning

### Modell hittas inte
```python
model = manager.get_model("fel-nyckel")
if model is None:
    print("Modellen finns inte!")
    # Lista tillgängliga modeller
    print(manager.list_all_models())
```

### Provider inte tillgänglig
```python
from src.services.ai_providers.factory import AIProviderFactory

settings = get_settings()
available = AIProviderFactory.get_available_providers(settings)
print(f"Tillgängliga providers: {available}")
```

### Ladda om konfiguration
```python
# Om du ändrar models.yaml under körning
from src.core.model_config import ModelConfigManager

# Skapa ny instance (ej cache)
manager = ModelConfigManager()
```

## 🎨 Exempel: Välj modell dynamiskt

```python
from src.core.model_config import get_model_config_manager

def välj_modell_för_uppgift(uppgift_typ: str, max_kostnad: str = "medel"):
    """Välj bästa modellen för en uppgift"""
    manager = get_model_config_manager()
    
    # Få rekommendationer för användningsfall
    rekommenderade = manager.get_recommended_models(uppgift_typ)
    
    if not rekommenderade:
        return "lokal"  # Fallback
    
    # Filtrera på kostnad
    for model_key in rekommenderade:
        model = manager.get_model(model_key)
        if model and model.kostnad in ["gratis", "låg", max_kostnad]:
            return model_key
    
    return rekommenderade[0]  # Första rekommendationen

# Användning
modell = välj_modell_för_uppgift("snabba_svar", max_kostnad="låg")
print(f"Vald modell: {modell}")
```

## 📚 API-referens

### ModelConfig (dataclass)
```python
@dataclass
class ModelConfig:
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
```

### ModelConfigManager

#### Metoder

- `get_model(model_key: str) -> Optional[ModelConfig]`
- `get_model_by_id(model_id: str) -> Optional[ModelConfig]`
- `get_models_by_provider(provider: str) -> List[ModelConfig]`
- `get_model_for_profile(profile_name: str) -> Optional[str]`
- `get_fallback_models(profile_name: str) -> List[str]`
- `get_recommended_models(användningsfall: str) -> List[str]`
- `list_all_models() -> Dict[str, str]`
- `get_model_info(model_key: str) -> Dict[str, Any]`
- `filter_models(...) -> List[str]`

## ✅ Fördelar med systemet

1. **Centraliserad konfiguration** - Alla modeller på ett ställe
2. **Enkel hantering** - CLI-verktyg och API
3. **Flexibel filtrering** - Hitta rätt modell för behov
4. **Automatisk fallback** - Robust felhantering
5. **Utbyggbart** - Lätt att lägga till nya modeller
6. **Type-safe** - Dataclasses och type hints
7. **Cached** - Effektiv prestanda

---

**🎯 Nu är det enkelt att hantera och konfigurera AI-modeller i IRIS!**
