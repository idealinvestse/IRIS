"""
IRIS v6.0 - User Models
Pydantic modeller för användare och GDPR-samtycke
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserConsent(BaseModel):
    """GDPR-samtycke"""
    user_id: str
    analytics: bool = False
    data_processing: bool = False
    given_at: Optional[datetime] = None
    
class UserProfile(BaseModel):
    """Användarprofil"""
    user_id: str
    preferred_profile: Optional[str] = "smart"
    language: str = "sv"
    timezone: str = "Europe/Stockholm"
    
class UserDataExport(BaseModel):
    """Data-export för GDPR portabilitet"""
    user_id: str
    queries: list = []
    consent_records: list = []
    export_timestamp: str
    format: str = "json"
