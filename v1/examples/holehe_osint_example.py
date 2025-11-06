"""
IRIS v6.0 - Holehe OSINT Example
Email verification and OSINT demonstration
"""

import asyncio
import logging
from pathlib import Path
import json

from src.services.holehe_osint import (
    HoleheService,
    HoleheException,
    HoleheNotInstalledException
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_single_email():
    """Example: Check a single email address."""
    logger.info("=" * 60)
    logger.info("Example 1: Single Email Check")
    logger.info("=" * 60)
    
    # Initialize service
    service = HoleheService(timeout=30, max_concurrent=10)
    
    # Check if holehe is available
    if not service.is_available():
        logger.error("❌ Holehe is not installed!")
        logger.info("Install with: pip install holehe")
        return
    
    try:
        # Check email (use a test email or your own)
        email = "test@example.com"
        
        logger.info(f"Checking email: {email}")
        response = await service.check_email(email)
        
        # Display results
        logger.info("\n📊 Check Results:")
        logger.info(f"  Email: {response.email}")
        logger.info(f"  Total services checked: {response.total_checked}")
        logger.info(f"  Found on: {response.found_on} services")
        logger.info(f"  Rate limited: {response.rate_limited} services")
        logger.info(f"  Duration: {response.duration_seconds:.1f}s")
        
        logger.info("\n📍 Accounts found on:")
        for result in response.results:
            if result.exists:
                logger.info(f"  ✅ {result.name}")
                if result.email_recovery:
                    logger.info(f"     Recovery email: {result.email_recovery}")
                if result.phone_number:
                    logger.info(f"     Recovery phone: {result.phone_number}")
        
        logger.info(f"\n⏱️ Rate limited services:")
        for result in response.results:
            if result.rate_limit:
                logger.info(f"  ⚠️ {result.name}")
        
        # Create email profile
        profile = service.create_email_profile(response)
        
        logger.info("\n👤 Email Profile:")
        logger.info(f"  Total accounts: {profile.total_accounts}")
        logger.info(f"  Risk score: {profile.risk_score}/100")
        logger.info(f"  Social media: {profile.has_social_media}")
        logger.info(f"  Professional: {profile.has_professional}")
        logger.info(f"  Gaming: {profile.has_gaming}")
        logger.info(f"  Shopping: {profile.has_shopping}")
        
        if profile.recovery_hints:
            logger.info(f"\n🔍 Recovery hints found:")
            for hint in profile.recovery_hints:
                logger.info(f"  {hint}")
        
        # Save results
        output_dir = Path("data/holehe_osint")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{email.replace('@', '_at_')}_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(response.model_dump(mode='json'), f, indent=2)
        
        logger.info(f"\n💾 Results saved to: {output_file}")
    
    except HoleheNotInstalledException as e:
        logger.error(f"❌ {e}")
    
    except HoleheException as e:
        logger.error(f"❌ Error: {e}")
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)


async def example_specific_modules():
    """Example: Check specific modules only."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Check Specific Modules")
    logger.info("=" * 60)
    
    service = HoleheService()
    
    if not service.is_available():
        logger.error("❌ Holehe is not installed!")
        return
    
    try:
        email = "test@example.com"
        
        # Check only specific services
        modules = ["twitter", "instagram", "facebook", "linkedin", "github"]
        
        logger.info(f"Checking {len(modules)} specific modules for: {email}")
        response = await service.check_email(email, modules=modules)
        
        logger.info(f"\n📊 Results:")
        logger.info(f"  Checked: {response.total_checked} services")
        logger.info(f"  Found: {response.found_on} accounts")
        
        for result in response.results:
            status = "✅" if result.exists else "❌"
            logger.info(f"  {status} {result.name}")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")


async def example_bulk_check():
    """Example: Check multiple emails."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Bulk Email Check")
    logger.info("=" * 60)
    
    service = HoleheService()
    
    if not service.is_available():
        logger.error("❌ Holehe is not installed!")
        return
    
    try:
        # Multiple emails to check
        emails = [
            "test1@example.com",
            "test2@example.com",
            "test3@example.com"
        ]
        
        logger.info(f"Bulk checking {len(emails)} emails...")
        
        # Check with limited modules for speed
        modules = ["twitter", "instagram", "linkedin"]
        
        response = await service.check_emails_bulk(
            emails=emails,
            modules=modules,
            concurrent_checks=2  # Check 2 emails at a time
        )
        
        logger.info(f"\n📊 Bulk Results:")
        logger.info(f"  Total emails: {response.total_emails}")
        logger.info(f"  Completed: {response.completed}")
        logger.info(f"  Failed: {response.failed}")
        logger.info(f"  Duration: {response.duration_seconds:.1f}s")
        
        logger.info(f"\n📧 Individual results:")
        for email_result in response.results:
            logger.info(f"\n  {email_result.email}:")
            logger.info(f"    Found on: {email_result.found_on}/{email_result.total_checked} services")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")


async def example_available_modules():
    """Example: List available modules."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Available Modules")
    logger.info("=" * 60)
    
    service = HoleheService()
    
    if not service.is_available():
        logger.error("❌ Holehe is not installed!")
        return
    
    try:
        modules = service.get_available_modules()
        
        logger.info(f"\n📋 Found {len(modules)} available modules:")
        
        # Group by category
        by_category = {}
        for module in modules:
            if module.category not in by_category:
                by_category[module.category] = []
            by_category[module.category].append(module.name)
        
        for category, module_names in sorted(by_category.items()):
            logger.info(f"\n  {category.upper()}:")
            for name in sorted(module_names):
                logger.info(f"    - {name}")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")


async def example_risk_analysis():
    """Example: Analyze risk based on email exposure."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: Risk Analysis")
    logger.info("=" * 60)
    
    service = HoleheService()
    
    if not service.is_available():
        logger.error("❌ Holehe is not installed!")
        return
    
    try:
        email = "test@example.com"
        
        logger.info(f"Analyzing risk for: {email}")
        response = await service.check_email(email)
        profile = service.create_email_profile(response)
        
        logger.info(f"\n🛡️ Risk Analysis:")
        logger.info(f"  Total accounts: {profile.total_accounts}")
        logger.info(f"  Risk score: {profile.risk_score}/100")
        
        # Risk level
        if profile.risk_score < 25:
            risk_level = "LOW ✅"
        elif profile.risk_score < 50:
            risk_level = "MODERATE ⚠️"
        elif profile.risk_score < 75:
            risk_level = "HIGH ⚠️"
        else:
            risk_level = "CRITICAL 🔴"
        
        logger.info(f"  Risk level: {risk_level}")
        
        logger.info(f"\n📊 Account categories:")
        for category in profile.categories:
            logger.info(f"  {category.category}: {category.found_count} accounts")
            logger.info(f"    Services: {', '.join(category.services)}")
        
        if profile.recovery_hints:
            logger.info(f"\n⚠️ Exposure: Recovery information found")
            logger.info(f"  This indicates the email is actively used")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")


async def main():
    """Run all examples."""
    logger.info("🚀 Holehe OSINT Examples")
    logger.info("⚠️  Note: Requires holehe to be installed (pip install holehe)\n")
    
    # Run examples
    await example_single_email()
    # await example_specific_modules()
    # await example_bulk_check()
    # await example_available_modules()
    # await example_risk_analysis()
    
    logger.info("\n" + "=" * 60)
    logger.info("💡 Tips:")
    logger.info("  - Uncomment examples above to run")
    logger.info("  - Replace test emails with real ones")
    logger.info("  - Check data/holehe_osint/ for results")
    logger.info("  - Respect rate limits and privacy")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
