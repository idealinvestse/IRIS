"""
IRIS v6.0 - Svenska Datakällor
Integrationer med SCB, OMX, SMHI och svenska nyheter
"""

import logging
from typing import Dict, Any, Optional
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class SwedishSources:
    """
    Hanterar alla svenska datakällor
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        logger.info("🇸🇪 SwedishSources initialiserad")
    
    async def get_scb_data(self, query: str) -> Dict[str, Any]:
        """
        Hämta data från Statistiska centralbyrån (SCB)
        """
        logger.info("📊 Hämtar SCB-data")
        
        try:
            # För demo: returnera statisk data
            # I produktion skulle detta anropa SCB:s API
            return {
                "source": "SCB",
                "summary": "SCB-data för befolkning och ekonomi",
                "data": {
                    "befolkning": "10.5 miljoner invånare (2024)",
                    "arbetslöshet": "7.2% (senaste mätningen)",
                    "inflation": "3.1% årlig inflation"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Fel vid SCB-hämtning: {e}")
            return {"error": str(e), "available": False}
    
    async def get_omx_data(self) -> Dict[str, Any]:
        """
        Hämta OMX Stockholm index data
        """
        logger.info("📈 Hämtar OMX-data")
        
        try:
            # Använd Yahoo Finance API för OMX
            url = "https://query1.finance.yahoo.com/v8/finance/chart/^OMX"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extrahera relevant data
                        result = data.get("chart", {}).get("result", [{}])[0]
                        meta = result.get("meta", {})
                        
                        return {
                            "source": "OMX Stockholm",
                            "price": meta.get("regularMarketPrice"),
                            "previous_close": meta.get("previousClose"),
                            "change": meta.get("regularMarketPrice", 0) - meta.get("previousClose", 0),
                            "currency": meta.get("currency", "SEK"),
                            "timestamp": datetime.utcnow().isoformat(),
                            "available": True
                        }
                    else:
                        return {
                            "error": f"HTTP {response.status}",
                            "available": False
                        }
                        
        except Exception as e:
            logger.error(f"Fel vid OMX-hämtning: {e}")
            return {
                "source": "OMX Stockholm",
                "error": str(e),
                "available": False,
                # Fallback demo-data
                "price": 2450.5,
                "previous_close": 2438.2,
                "change": 12.3,
                "currency": "SEK",
                "note": "Demo-data (API otillgängligt)"
            }
    
    async def get_swedish_news(self, query: str) -> Dict[str, Any]:
        """
        Hämta svenska nyheter från NewsData.io eller liknande
        """
        logger.info("📰 Hämtar svenska nyheter")
        
        try:
            if not self.settings.news_api_key or self.settings.news_api_key == "demo":
                # Demo-data om ingen API-nyckel
                return {
                    "source": "Svenska Nyheter",
                    "headlines": [
                        "Svensk ekonomi fortsätter växa - SCB",
                        "OMX når nya höjder på Stockholmsbörsen",
                        "SMHI varnar för kraftigt väder i norra Sverige",
                        "Ny statistik visar ökad sysselsättning"
                    ],
                    "count": 4,
                    "timestamp": datetime.utcnow().isoformat(),
                    "available": True,
                    "note": "Demo-data (ingen API-nyckel konfigurerad)"
                }
            
            # Med riktig API-nyckel skulle vi anropa NewsData.io här
            url = "https://newsdata.io/api/1/news"
            params = {
                "apikey": self.settings.news_api_key,
                "language": "sv",
                "q": query,
                "country": "se"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get("results", [])
                        
                        return {
                            "source": "Svenska Nyheter",
                            "headlines": [article.get("title") for article in articles[:5]],
                            "count": len(articles),
                            "timestamp": datetime.utcnow().isoformat(),
                            "available": True
                        }
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Fel vid nyhetshämtning: {e}")
            return {
                "source": "Svenska Nyheter",
                "error": str(e),
                "available": False
            }
    
    async def get_smhi_data(self, query: str) -> Dict[str, Any]:
        """
        Hämta väderdata från SMHI
        """
        logger.info("🌤️ Hämtar SMHI väderdata")
        
        try:
            # För demo: enkel väderdata
            # I produktion skulle detta anropa SMHI:s öppna API
            
            # Extrahera plats från query om möjligt
            location = "Stockholm"  # Default
            if "göteborg" in query.lower():
                location = "Göteborg"
            elif "malmö" in query.lower():
                location = "Malmö"
            
            return {
                "source": "SMHI",
                "location": location,
                "forecast": f"Delvis molnigt, 12°C i {location}",
                "temperature": 12,
                "conditions": "Delvis molnigt",
                "wind": "5 m/s",
                "humidity": "65%",
                "timestamp": datetime.utcnow().isoformat(),
                "available": True,
                "note": "Generisk väderdata (demo)"
            }
            
        except Exception as e:
            logger.error(f"Fel vid SMHI-hämtning: {e}")
            return {
                "source": "SMHI",
                "error": str(e),
                "available": False
            }
