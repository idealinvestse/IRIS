"""
IRIS v6.0 - Holehe OSINT Models
Pydantic models for email verification and OSINT data
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class HoleheResult(BaseModel):
    """
    Individual result from a holehe module check.
    
    Each module checks one website/service.
    """
    name: str = Field(..., description="Service/website name")
    exists: bool = Field(..., description="Email is registered on this service")
    rate_limit: bool = Field(False, description="Rate limited by service")
    email_recovery: Optional[str] = Field(None, description="Partial recovery email")
    phone_number: Optional[str] = Field(None, description="Partial recovery phone")
    others: Optional[Dict[str, Any]] = Field(None, description="Additional information")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "name": "twitter",
                "exists": True,
                "rate_limit": False,
                "email_recovery": "ex****e@gmail.com",
                "phone_number": "0*******78",
                "others": None
            }
        }


class EmailCheckRequest(BaseModel):
    """Request model for email verification."""
    email: EmailStr = Field(..., description="Email address to check")
    modules: Optional[List[str]] = Field(
        None,
        description="Specific modules to check (None = all)"
    )
    timeout: int = Field(30, ge=5, le=120, description="Timeout per module in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "modules": ["twitter", "instagram", "facebook"],
                "timeout": 30
            }
        }


class EmailCheckResponse(BaseModel):
    """Response model for email verification."""
    email: str = Field(..., description="Checked email address")
    total_checked: int = Field(0, description="Total services checked")
    found_on: int = Field(0, description="Number of services where email exists")
    rate_limited: int = Field(0, description="Number of rate-limited services")
    results: List[HoleheResult] = Field(
        default_factory=list,
        description="Detailed results per service"
    )
    duration_seconds: float = Field(0.0, description="Total check duration")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Check timestamp"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "total_checked": 120,
                "found_on": 15,
                "rate_limited": 2,
                "results": [],
                "duration_seconds": 45.3,
                "timestamp": "2025-11-06T04:00:00"
            }
        }


class ServiceCategory(BaseModel):
    """Category grouping for services."""
    category: str = Field(..., description="Category name")
    services: List[str] = Field(default_factory=list, description="Service names")
    found_count: int = Field(0, description="Count of found accounts in category")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "category": "social_media",
                "services": ["twitter", "instagram", "facebook"],
                "found_count": 2
            }
        }


class EmailProfile(BaseModel):
    """
    Aggregated email profile from all checks.
    
    Provides a comprehensive view of the email's online presence.
    """
    email: str = Field(..., description="Email address")
    total_accounts: int = Field(0, description="Total accounts found")
    categories: List[ServiceCategory] = Field(
        default_factory=list,
        description="Accounts by category"
    )
    has_social_media: bool = Field(False, description="Has social media accounts")
    has_professional: bool = Field(False, description="Has professional accounts")
    has_gaming: bool = Field(False, description="Has gaming accounts")
    has_shopping: bool = Field(False, description="Has shopping accounts")
    risk_score: int = Field(
        0,
        ge=0,
        le=100,
        description="Risk score (0-100, higher = more exposed)"
    )
    recovery_hints: List[str] = Field(
        default_factory=list,
        description="Partial recovery emails/phones found"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "total_accounts": 15,
                "categories": [],
                "has_social_media": True,
                "has_professional": True,
                "risk_score": 65,
                "recovery_hints": ["ex****e@gmail.com"]
            }
        }


class BulkEmailCheckRequest(BaseModel):
    """Request model for bulk email checks."""
    emails: List[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of emails to check"
    )
    modules: Optional[List[str]] = Field(
        None,
        description="Specific modules to check"
    )
    concurrent_checks: int = Field(
        5,
        ge=1,
        le=10,
        description="Max concurrent email checks"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "emails": ["test1@example.com", "test2@example.com"],
                "modules": ["twitter", "instagram"],
                "concurrent_checks": 5
            }
        }


class BulkEmailCheckResponse(BaseModel):
    """Response model for bulk email checks."""
    total_emails: int = Field(0, description="Total emails checked")
    completed: int = Field(0, description="Successfully completed checks")
    failed: int = Field(0, description="Failed checks")
    results: List[EmailCheckResponse] = Field(
        default_factory=list,
        description="Results per email"
    )
    duration_seconds: float = Field(0.0, description="Total duration")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "total_emails": 10,
                "completed": 9,
                "failed": 1,
                "results": [],
                "duration_seconds": 120.5
            }
        }


class AvailableModule(BaseModel):
    """Information about an available holehe module."""
    name: str = Field(..., description="Module name")
    category: str = Field(..., description="Category")
    description: Optional[str] = Field(None, description="Module description")
    is_active: bool = Field(True, description="Module is active")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "name": "twitter",
                "category": "social_media",
                "description": "Twitter/X social network",
                "is_active": True
            }
        }
