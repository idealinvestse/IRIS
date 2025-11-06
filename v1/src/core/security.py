"""
IRIS v6.0 - Säkerhets- och GDPR-hantering
Hanterar användarsamtycke, dataskydd och säkerhetsvalidering
"""

import hashlib
import logging
import re
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Hanterar säkerhet och GDPR-efterlevnad för IRIS v6.0
    """
    
    def __init__(self):
        from src.core.config import get_settings
        self.settings = get_settings()
        self.cipher = None
        
        # Initialisera kryptering om nyckel finns
        if self.settings.encryption_key:
            try:
                self.cipher = Fernet(self.settings.encryption_key.encode())
            except Exception as e:
                logger.warning(f"Kunde inte initialisera kryptering: {e}")
        
        logger.info("🔒 SecurityManager initialiserad")
    
    async def verify_gdpr_consent(self, user_id: str = "anonym") -> bool:
        """
        Verifiera GDPR-samtycke för användare
        Returnerar True om GDPR är inaktiverat eller om samtycke finns
        """
        # Om GDPR inte är aktiverat, tillåt alltid
        if not self.settings.gdpr_enabled:
            return True
        
        # Anonyma användare behöver inte samtycke för läsoperationer
        if user_id == "anonym":
            return True
        
        # Hämta samtycke från databas
        try:
            from src.core.database import Database
            db = Database()
            consent = await db.get_consent(user_id)
            
            if consent and consent.get("data_processing"):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Fel vid samtyckes-verifiering: {e}")
            # I händelse av fel, tillåt INTE åtkomst
            return False
    
    async def validate_request(self, request: Request, query_request: Any):
        """
        Validera inkommande request för säkerhet
        """
        # Kontrollera att frågan inte är för lång
        if len(query_request.query) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Frågan är för lång. Max 1000 tecken."
            )
        
        # Kontrollera för potentiella injektioner
        if self._contains_injection_patterns(query_request.query):
            logger.warning(f"⚠️ Potentiell injektionsattack upptäckt: {query_request.query[:50]}")
            raise HTTPException(
                status_code=400,
                detail="Ogiltig input upptäckt"
            )
        
        # Rate limiting skulle implementeras här
        # För nu, logga bara
        client_ip = request.client.host if request.client else "unknown"
        logger.debug(f"Request från IP: {client_ip}")
    
    def _contains_injection_patterns(self, text: str) -> bool:
        """
        Enkel kontroll för SQL/Script injection-mönster
        """
        patterns = [
            r"<script",
            r"javascript:",
            r"on\w+\s*=",
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from"
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def hash_query(self, query: str) -> str:
        """
        Skapa SHA-256 hash av fråga för GDPR-kompatibel loggning
        """
        return hashlib.sha256(query.encode('utf-8')).hexdigest()
    
    def anonymize_user_id(self, user_id: str) -> str:
        """
        Anonymisera användar-ID för loggning
        """
        if user_id == "anonym":
            return "anonym"
        
        # Returnera hashad version
        return hashlib.sha256(user_id.encode('utf-8')).hexdigest()[:16]
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Kryptera känslig data
        """
        if not self.cipher:
            logger.warning("Kryptering inte tillgänglig, returnerar okrypterad data")
            return data
        
        try:
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Krypteringsfel: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Dekryptera känslig data
        """
        if not self.cipher:
            logger.warning("Dekryptering inte tillgänglig")
            return encrypted_data
        
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Dekrypteringsfel: {e}")
            return encrypted_data
    
    async def update_consent(self, user_id: str, consent_data: Dict[str, bool]):
        """
        Uppdatera användarens GDPR-samtycke
        """
        try:
            from src.core.database import Database
            db = Database()
            
            await db.update_consent(
                user_id=user_id,
                analytics=consent_data.get("analytics", False),
                data_processing=consent_data.get("data_processing", False)
            )
            
            logger.info(f"✅ Samtycke uppdaterat för användare: {self.anonymize_user_id(user_id)}")
            
        except Exception as e:
            logger.error(f"Kunde inte uppdatera samtycke: {e}")
            raise
    
    def sanitize_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanera output för att ta bort känslig information
        """
        # Ta bort eventuella API-nycklar som läckt in i output
        sensitive_patterns = [
            r"xai-[A-Za-z0-9]+",
            r"sk-[A-Za-z0-9]+",
            r"Bearer [A-Za-z0-9]+",
        ]
        
        def clean_value(value):
            if isinstance(value, str):
                for pattern in sensitive_patterns:
                    value = re.sub(pattern, "***API_KEY***", value)
                return value
            elif isinstance(value, dict):
                return {k: clean_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [clean_value(item) for item in value]
            return value
        
        return clean_value(data)
    
    def validate_api_key(self, api_key: str, service: str) -> bool:
        """
        Validera API-nyckelformat
        """
        patterns = {
            "xai": r"^xai-[A-Za-z0-9]{40,}$",
            "openai": r"^sk-[A-Za-z0-9]{40,}$",
            "news": r"^[A-Za-z0-9]{20,}$"
        }
        
        pattern = patterns.get(service)
        if not pattern:
            return True  # Okänd tjänst, tillåt
        
        return bool(re.match(pattern, api_key))
    
    def get_gdpr_info(self) -> Dict[str, Any]:
        """
        Returnera GDPR-information
        """
        return {
            "gdpr_aktiverat": self.settings.gdpr_enabled,
            "datalagring_dagar": self.settings.data_retention_days,
            "kryptering_aktiv": self.cipher is not None,
            "användarrättigheter": {
                "rätt_till_tillgång": True,
                "rätt_till_rättelse": True,
                "rätt_till_radering": True,
                "rätt_till_dataportabilitet": True,
                "rätt_att_göra_invändningar": True
            },
            "kontakt": {
                "dataskyddsombud": "dpo@iris.se",
                "support": "support@iris.se"
            }
        }
