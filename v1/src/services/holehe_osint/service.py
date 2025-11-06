"""
IRIS v6.0 - Holehe OSINT Service
Email verification and OSINT using holehe
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime
import importlib
import pkgutil

from .models import (
    HoleheResult,
    EmailCheckResponse,
    EmailProfile,
    ServiceCategory,
    AvailableModule,
    BulkEmailCheckResponse
)

logger = logging.getLogger(__name__)


class HoleheException(Exception):
    """Base exception for Holehe service."""
    pass


class HoleheNotInstalledException(HoleheException):
    """Exception when holehe is not installed."""
    pass


class HoleheService:
    """
    Holehe OSINT service for email verification.
    
    Features:
    - Check if email is registered on 120+ websites
    - Social media, professional networks, gaming platforms
    - Bulk email checking with concurrency control
    - Profile aggregation and risk scoring
    - GDPR compliant (only uses public forgot password APIs)
    """
    
    # Service categories for organization
    CATEGORIES = {
        "social_media": [
            "twitter", "instagram", "facebook", "snapchat", "tiktok",
            "linkedin", "pinterest", "reddit", "tumblr"
        ],
        "professional": [
            "linkedin", "github", "gitlab", "stackoverflow", "indeed"
        ],
        "gaming": [
            "steam", "epicgames", "twitch", "discord", "xbox", "playstation"
        ],
        "shopping": [
            "amazon", "ebay", "etsy", "aliexpress", "paypal"
        ],
        "communication": [
            "skype", "telegram", "whatsapp", "viber", "discord"
        ],
        "entertainment": [
            "spotify", "netflix", "hulu", "disney", "youtube"
        ],
        "other": []
    }
    
    def __init__(
        self,
        timeout: int = 30,
        max_concurrent: int = 10,
        retry_on_rate_limit: bool = False
    ):
        """
        Initialize HoleheService.
        
        Args:
            timeout: Timeout per module check in seconds
            max_concurrent: Max concurrent module checks
            retry_on_rate_limit: Retry if rate limited
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.retry_on_rate_limit = retry_on_rate_limit
        self._holehe_available = self._check_holehe_installed()
        
        if self._holehe_available:
            logger.info(
                f"🔍 HoleheService initialized: "
                f"timeout={timeout}s, max_concurrent={max_concurrent}"
            )
        else:
            logger.warning(
                "⚠️ Holehe not installed. Install with: pip install holehe"
            )
    
    def _check_holehe_installed(self) -> bool:
        """Check if holehe is installed."""
        try:
            import holehe
            return True
        except ImportError:
            return False
    
    async def check_email(
        self,
        email: str,
        modules: Optional[List[str]] = None
    ) -> EmailCheckResponse:
        """
        Check if email is registered on various services.
        
        Args:
            email: Email address to check
            modules: Specific modules to check (None = all)
        
        Returns:
            EmailCheckResponse with results
        
        Raises:
            HoleheNotInstalledException: If holehe is not installed
            HoleheException: On check errors
        """
        if not self._holehe_available:
            raise HoleheNotInstalledException(
                "Holehe is not installed. Install with: pip install holehe"
            )
        
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        
        logger.info(f"🔍 Checking email: {email}")
        start_time = datetime.now()
        
        try:
            import trio
            import httpx
            from holehe import modules as holehe_modules
            
            results = []
            
            async def run_check():
                """Run holehe checks using trio."""
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # Get available modules
                    available = self._get_available_modules()
                    
                    # Filter modules if specified
                    if modules:
                        available = [
                            m for m in available 
                            if m.name in modules
                        ]
                    
                    logger.info(
                        f"Checking {len(available)} modules for {email}"
                    )
                    
                    # Run checks
                    for module_info in available:
                        try:
                            # Dynamically import module
                            module_path = f"holehe.modules.{module_info.category}.{module_info.name}"
                            module = importlib.import_module(module_path)
                            
                            # Get the check function
                            check_func = getattr(module, module_info.name)
                            
                            # Run check
                            out = []
                            await check_func(email, client, out)
                            
                            # Parse results
                            if out:
                                result_data = out[0]
                                result = HoleheResult(
                                    name=result_data.get("name", module_info.name),
                                    exists=result_data.get("exists", False),
                                    rate_limit=result_data.get("rateLimit", False),
                                    email_recovery=result_data.get("emailrecovery"),
                                    phone_number=result_data.get("phoneNumber"),
                                    others=result_data.get("others")
                                )
                                results.append(result)
                            
                        except Exception as e:
                            logger.debug(
                                f"Error checking {module_info.name}: {e}"
                            )
            
            # Run trio async
            trio.from_thread.run_sync(run_check)
            
            # Calculate statistics
            found_on = sum(1 for r in results if r.exists)
            rate_limited = sum(1 for r in results if r.rate_limit)
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"✅ Email check complete: {email} - "
                f"Found on {found_on}/{len(results)} services "
                f"({duration:.1f}s)"
            )
            
            return EmailCheckResponse(
                email=email,
                total_checked=len(results),
                found_on=found_on,
                rate_limited=rate_limited,
                results=results,
                duration_seconds=duration
            )
        
        except Exception as e:
            logger.error(f"Failed to check email {email}: {e}", exc_info=True)
            raise HoleheException(f"Email check failed: {e}")
    
    async def check_emails_bulk(
        self,
        emails: List[str],
        modules: Optional[List[str]] = None,
        concurrent_checks: int = 5
    ) -> BulkEmailCheckResponse:
        """
        Check multiple emails concurrently.
        
        Args:
            emails: List of email addresses
            modules: Specific modules to check
            concurrent_checks: Max concurrent email checks
        
        Returns:
            BulkEmailCheckResponse with all results
        """
        if not emails:
            raise ValueError("Emails list cannot be empty")
        
        logger.info(f"🔍 Bulk checking {len(emails)} emails")
        start_time = datetime.now()
        
        results = []
        failed = 0
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_checks)
        
        async def check_with_semaphore(email: str):
            """Check email with semaphore."""
            async with semaphore:
                try:
                    return await self.check_email(email, modules)
                except Exception as e:
                    logger.error(f"Failed to check {email}: {e}")
                    return None
        
        # Run checks concurrently
        tasks = [check_with_semaphore(email) for email in emails]
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in check_results:
            if isinstance(result, EmailCheckResponse):
                results.append(result)
            else:
                failed += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"✅ Bulk check complete: {len(results)}/{len(emails)} succeeded "
            f"({duration:.1f}s)"
        )
        
        return BulkEmailCheckResponse(
            total_emails=len(emails),
            completed=len(results),
            failed=failed,
            results=results,
            duration_seconds=duration
        )
    
    def create_email_profile(
        self,
        response: EmailCheckResponse
    ) -> EmailProfile:
        """
        Create aggregated email profile from check response.
        
        Args:
            response: EmailCheckResponse from check_email
        
        Returns:
            EmailProfile with categorized data
        """
        # Group results by category
        categories = []
        recovery_hints = []
        
        for category_name, service_names in self.CATEGORIES.items():
            found_services = [
                r.name for r in response.results
                if r.name in service_names and r.exists
            ]
            
            if found_services:
                categories.append(ServiceCategory(
                    category=category_name,
                    services=found_services,
                    found_count=len(found_services)
                ))
        
        # Collect recovery hints
        for result in response.results:
            if result.email_recovery:
                recovery_hints.append(f"Email: {result.email_recovery}")
            if result.phone_number:
                recovery_hints.append(f"Phone: {result.phone_number}")
        
        # Calculate presence flags
        has_social_media = any(
            c.category == "social_media" for c in categories
        )
        has_professional = any(
            c.category == "professional" for c in categories
        )
        has_gaming = any(
            c.category == "gaming" for c in categories
        )
        has_shopping = any(
            c.category == "shopping" for c in categories
        )
        
        # Calculate risk score (more accounts = higher exposure)
        risk_score = min(100, response.found_on * 5)  # 5 points per account
        
        return EmailProfile(
            email=response.email,
            total_accounts=response.found_on,
            categories=categories,
            has_social_media=has_social_media,
            has_professional=has_professional,
            has_gaming=has_gaming,
            has_shopping=has_shopping,
            risk_score=risk_score,
            recovery_hints=list(set(recovery_hints))  # Remove duplicates
        )
    
    def _get_available_modules(self) -> List[AvailableModule]:
        """
        Get list of available holehe modules.
        
        Returns:
            List of AvailableModule objects
        """
        modules = []
        
        try:
            import holehe.modules as holehe_modules_pkg
            
            # Iterate through categories
            for category in ["social_media", "entertainment", "gaming", "shopping"]:
                try:
                    category_module = importlib.import_module(
                        f"holehe.modules.{category}"
                    )
                    
                    # Get all modules in category
                    for importer, modname, ispkg in pkgutil.iter_modules(
                        category_module.__path__
                    ):
                        modules.append(AvailableModule(
                            name=modname,
                            category=category,
                            description=f"{modname.title()} service check",
                            is_active=True
                        ))
                
                except ImportError:
                    pass
        
        except ImportError:
            logger.warning("Could not load holehe modules")
        
        return modules
    
    def get_available_modules(self) -> List[AvailableModule]:
        """
        Get list of available holehe modules (public method).
        
        Returns:
            List of AvailableModule objects
        """
        return self._get_available_modules()
    
    def is_available(self) -> bool:
        """Check if holehe is available."""
        return self._holehe_available
