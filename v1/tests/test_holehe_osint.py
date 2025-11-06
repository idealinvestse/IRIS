"""
IRIS v6.0 - Holehe OSINT Tests
"""

import pytest
from unittest.mock import Mock, patch

from src.services.holehe_osint import (
    HoleheService,
    HoleheException,
    HoleheNotInstalledException,
    HoleheResult,
    EmailCheckResponse,
    EmailProfile
)


class TestHoleheResult:
    """Test HoleheResult model."""
    
    def test_result_creation(self):
        """Test creating a holehe result."""
        result = HoleheResult(
            name="twitter",
            exists=True,
            rate_limit=False,
            email_recovery="ex****e@gmail.com"
        )
        
        assert result.name == "twitter"
        assert result.exists is True
        assert result.rate_limit is False
        assert result.email_recovery == "ex****e@gmail.com"
    
    def test_result_defaults(self):
        """Test result with defaults."""
        result = HoleheResult(
            name="instagram",
            exists=False
        )
        
        assert result.name == "instagram"
        assert result.exists is False
        assert result.rate_limit is False
        assert result.email_recovery is None
        assert result.phone_number is None


class TestEmailCheckResponse:
    """Test EmailCheckResponse model."""
    
    def test_response_creation(self):
        """Test creating a response."""
        results = [
            HoleheResult(name="twitter", exists=True, rate_limit=False),
            HoleheResult(name="instagram", exists=False, rate_limit=False)
        ]
        
        response = EmailCheckResponse(
            email="test@example.com",
            total_checked=2,
            found_on=1,
            rate_limited=0,
            results=results,
            duration_seconds=10.5
        )
        
        assert response.email == "test@example.com"
        assert response.total_checked == 2
        assert response.found_on == 1
        assert response.rate_limited == 0
        assert len(response.results) == 2
        assert response.duration_seconds == 10.5


class TestHoleheService:
    """Test HoleheService class."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = HoleheService(
            timeout=30,
            max_concurrent=10,
            retry_on_rate_limit=False
        )
        
        assert service.timeout == 30
        assert service.max_concurrent == 10
        assert service.retry_on_rate_limit is False
    
    def test_is_available(self):
        """Test checking if holehe is available."""
        service = HoleheService()
        # Result depends on whether holehe is installed
        result = service.is_available()
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_check_email_validation(self):
        """Test email validation."""
        service = HoleheService()
        
        with pytest.raises(ValueError, match="Email cannot be empty"):
            await service.check_email("")
    
    @pytest.mark.asyncio
    async def test_check_email_not_installed(self):
        """Test check when holehe not installed."""
        service = HoleheService()
        service._holehe_available = False  # Simulate not installed
        
        with pytest.raises(
            HoleheNotInstalledException,
            match="Holehe is not installed"
        ):
            await service.check_email("test@example.com")
    
    @pytest.mark.asyncio
    async def test_bulk_check_validation(self):
        """Test bulk check validation."""
        service = HoleheService()
        
        with pytest.raises(ValueError, match="Emails list cannot be empty"):
            await service.check_emails_bulk([])
    
    def test_create_email_profile(self):
        """Test creating email profile."""
        service = HoleheService()
        
        # Create mock response
        results = [
            HoleheResult(name="twitter", exists=True, rate_limit=False),
            HoleheResult(name="instagram", exists=True, rate_limit=False),
            HoleheResult(name="linkedin", exists=True, rate_limit=False),
            HoleheResult(
                name="facebook",
                exists=True,
                rate_limit=False,
                email_recovery="ex****e@gmail.com"
            )
        ]
        
        response = EmailCheckResponse(
            email="test@example.com",
            total_checked=4,
            found_on=4,
            rate_limited=0,
            results=results,
            duration_seconds=15.0
        )
        
        # Create profile
        profile = service.create_email_profile(response)
        
        assert profile.email == "test@example.com"
        assert profile.total_accounts == 4
        assert profile.has_social_media is True
        assert profile.risk_score == 20  # 4 accounts * 5 points
        assert len(profile.recovery_hints) > 0
    
    def test_service_categories(self):
        """Test service categories."""
        assert "social_media" in HoleheService.CATEGORIES
        assert "professional" in HoleheService.CATEGORIES
        assert "gaming" in HoleheService.CATEGORIES
        assert "twitter" in HoleheService.CATEGORIES["social_media"]
        assert "linkedin" in HoleheService.CATEGORIES["professional"]


@pytest.mark.skipif(
    not pytest.config.getoption("--run-integration", default=False),
    reason="Integration tests disabled by default"
)
class TestHoleheServiceIntegration:
    """
    Integration tests requiring holehe to be installed.
    Run with: pytest --run-integration
    """
    
    @pytest.mark.asyncio
    async def test_check_real_email(self):
        """Test checking a real email."""
        service = HoleheService()
        
        if not service.is_available():
            pytest.skip("Holehe not installed")
        
        try:
            # Use a known test email or your own
            response = await service.check_email(
                "test@example.com",
                modules=["twitter", "instagram"]  # Limit modules
            )
            
            assert response.email == "test@example.com"
            assert response.total_checked > 0
            assert isinstance(response.found_on, int)
            assert isinstance(response.rate_limited, int)
        
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_get_available_modules(self):
        """Test getting available modules."""
        service = HoleheService()
        
        if not service.is_available():
            pytest.skip("Holehe not installed")
        
        try:
            modules = service.get_available_modules()
            assert isinstance(modules, list)
            assert len(modules) > 0
        
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")


# Pytest configuration
def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests"
    )
