"""
IRIS v6.0 - Briefing Models
Pydantic modeller för briefings och analyser
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class BriefingRequest(BaseModel):
    """Request-modell för briefing"""
    query: str = Field(..., min_length=3, max_length=1000, description="Fråga på svenska")
    user_id: str = Field(default="anonym", description="Användar-ID")
    profil: Optional[str] = Field(None, description="Önskad AI-profil")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SourceData(BaseModel):
    """Data från en källa"""
    source_name: str
    data: Dict[str, Any]
    available: bool
    timestamp: str
    error: Optional[str] = None

class BriefingResponse(BaseModel):
    """Response-modell för briefing"""
    success: bool
    query: str
    profile_used: str
    answer: str
    sources_used: List[str]
    processing_time: float
    timestamp: str
    confidence: Optional[float] = None
    model_used: Optional[str] = None
    
class AnalysisResult(BaseModel):
    """Resultat från AI-analys"""
    answer: str
    model: str
    tokens_used: int = 0
    confidence: float = 0.0
    sources: List[str] = []
