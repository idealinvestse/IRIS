# 🚀 Groq Cloud Quickstart - Kimi K2 Integration

## Snabbstart

### 1. Installera Groq SDK

```bash
pip install groq==0.11.0
```

### 2. Skaffa Groq API-nyckel

1. Gå till [https://console.groq.com](https://console.groq.com)
2. Registrera dig / Logga in
3. Skapa ny API-nyckel
4. Kopiera nyckeln (börjar med `gsk_...`)

### 3. Konfigurera .env

```bash
# Kopiera från exempel
cp .env.example .env

# Redigera .env och lägg till din Groq API-nyckel
GROQ_API_KEY=gsk_din_groq_api_nyckel_här
```

### 4. Testa Installation

```bash
# Kör servern
uvicorn src.main:app --reload

# I annat terminal-fönster, testa med snabb profil
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Vad är 2+2?",
    "profil": "snabb"
  }'
```

## 📊 Profiler och Providers

### Snabb Profil (Groq Kimi K2)
```bash
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hur är vädret i Stockholm?",
    "profil": "snabb"
  }'
```

**Använder:**
- Provider: Groq Cloud
- Modell: moonshotai/kimi-k2-instruct-0905
- Streaming: Ja
- Förväntad tid: < 2 sekunder

### Smart Profil (xAI Grok)
```bash
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analysera svenska ekonomin",
    "profil": "smart"
  }'
```

**Använder:**
- Provider: xAI
- Modell: grok-beta
- Streaming: Nej
- Förväntad tid: 3-7 sekunder

### Privat Profil (Lokal)
```bash
curl -X POST http://localhost:8000/analysera \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Privat analys",
    "profil": "privat"
  }'
```

**Använder:**
- Provider: Lokal regelbaserad
- Modell: lokal
- Streaming: Nej
- Förväntad tid: 5-15 sekunder
- Ingen extern kommunikation

## 🔧 Direkt Användning av Groq Provider

### Python Exempel

```python
from src.services.ai_providers.groq_provider import GroqProvider
import asyncio

async def test_groq():
    # Skapa provider
    provider = GroqProvider(
        api_key="gsk_din_nyckel",
        timeout=10
    )
    
    # Enkel analys
    result = await provider.analyze(
        query="Vad är huvudstaden i Sverige?",
        context="",
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.6,
        max_tokens=100
    )
    
    print(result["svar"])
    
    # Streaming
    print("\nStreaming:")
    async for chunk in provider.analyze_stream(
        query="Räkna till 5",
        context="",
        model="moonshotai/kimi-k2-instruct-0905"
    ):
        print(chunk, end="", flush=True)

# Kör
asyncio.run(test_groq())
```

## 📈 Prestanda

### Jämförelse

| Profil | Provider | Modell | Tid | Streaming |
|--------|----------|--------|-----|-----------|
| Snabb | Groq | Kimi K2 | < 2s | ✅ |
| Smart | xAI | Grok | 3-7s | ❌ |
| Privat | Lokal | Regelbaserad | 5-15s | ❌ |

### Kostnader (Groq)

Groq Cloud erbjuder mycket konkurrenskraftiga priser:
- Free tier: 30 requests/min
- Pay-as-you-go: $0.10-0.27 per 1M tokens

## 🧪 Testning

### Kör alla tester
```bash
pytest tests/test_groq_provider.py -v
```

### Kör med riktig API (kräver GROQ_API_KEY)
```bash
export GROQ_API_KEY=gsk_din_nyckel
pytest tests/test_groq_provider.py -v
```

### Test streaming
```bash
python -c "
from src.services.ai_providers.groq_provider import GroqProvider
import asyncio
import os

async def test():
    provider = GroqProvider(os.getenv('GROQ_API_KEY'))
    async for chunk in provider.analyze_stream('Hej, vem är du?', ''):
        print(chunk, end='', flush=True)

asyncio.run(test())
"
```

## 🔄 Fallback-Strategi

IRIS har automatisk fallback:

```
1. Groq (försök)
   ↓ (om fel)
2. xAI (fallback)
   ↓ (om fel)
3. Lokal (sista utväg - fungerar alltid)
```

### Testa Fallback

```python
from src.services.ai_analyzer_new import AIAnalyzer
import asyncio

async def test_fallback():
    analyzer = AIAnalyzer()
    
    # Om Groq misslyckas, fallback till xAI/lokal
    result = await analyzer.analyze(
        query="Test fråga",
        context_data={},
        profile="snabb",
        profile_config={
            "ai_provider": "groq",
            "ai_model": "moonshotai/kimi-k2-instruct-0905",
            "temperature": 0.6,
            "max_tokens": 100
        }
    )
    
    print(f"Använd provider: {result['provider']}")
    print(f"Svar: {result['svar']}")

asyncio.run(test_fallback())
```

## ⚙️ Konfiguration

### Ändra Profil-Inställningar

Redigera `config/profiles.yaml`:

```yaml
snabb:
  ai_provider: "groq"
  ai_model: "moonshotai/kimi-k2-instruct-0905"
  streaming: true
  temperature: 0.6  # Justera kreativitet
  max_tokens: 4096  # Max svar-längd
```

### Miljövariabler

```bash
# .env
GROQ_API_KEY=gsk_...
GROQ_TIMEOUT=10
GROQ_MODEL_DEFAULT=moonshotai/kimi-k2-instruct-0905
```

## 🐛 Troubleshooting

### Problem: "Groq API-nyckel saknas"

**Lösning:**
```bash
# Kontrollera .env
cat .env | grep GROQ_API_KEY

# Sätt om den saknas
echo "GROQ_API_KEY=gsk_din_nyckel" >> .env
```

### Problem: "Module 'groq' not found"

**Lösning:**
```bash
pip install groq==0.11.0
```

### Problem: "Rate limit exceeded"

**Lösning:**
- Vänta 60 sekunder (free tier: 30 req/min)
- Uppgradera till betald plan
- Använd fallback till xAI eller lokal

### Problem: Streaming fungerar inte

**Kontrollera:**
```python
# Ska vara True för streaming
profile_config["streaming"] = True

# Provider måste stödja streaming
# Groq: ✅ Ja
# xAI: ❌ Nej (använder non-streaming fallback)
# Lokal: Simulerad streaming
```

## 📚 Dokumentation

- **Groq Docs**: https://console.groq.com/docs
- **Kimi K2 Info**: https://platform.moonshot.cn
- **IRIS API Docs**: http://localhost:8000/dokumentation

## 🎉 Färdig!

Din IRIS installation använder nu Groq Cloud med Kimi K2 för ultrasnabba svar! 🚀
