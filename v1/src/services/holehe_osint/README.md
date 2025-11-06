# Holehe OSINT for IRIS v6.0

Email verification and OSINT (Open Source Intelligence) using holehe.

## Overview

Holehe is a powerful OSINT tool that checks if an email address is registered on 120+ websites and platforms including Twitter, Instagram, Facebook, LinkedIn, GitHub, and many more. It uses the "forgot password" function to verify registration without alerting the target email.

## Features

- ✅ **120+ Services** - Check Twitter, Instagram, LinkedIn, GitHub, Steam, and more
- ✅ **No Alerts** - Uses forgot password APIs without sending emails
- ✅ **Bulk Checking** - Check multiple emails concurrently
- ✅ **Risk Scoring** - Calculate exposure based on account count
- ✅ **Profile Aggregation** - Group findings by category
- ✅ **Recovery Hints** - Extract partial recovery emails/phones
- ✅ **GDPR Compliant** - Only uses public APIs
- ✅ **Rate Limit Handling** - Detects and handles rate limits

## Installation

```bash
# Holehe is included in requirements.txt
pip install holehe>=1.6.0
pip install trio>=0.24.0
```

## Architecture

```
src/services/holehe_osint/
├── __init__.py           # Module exports
├── models.py             # Pydantic data models
├── service.py            # Main HoleheService class
└── README.md             # This file
```

## Usage

### Basic Email Check

```python
from src.services.holehe_osint import HoleheService

# Initialize service
service = HoleheService(timeout=30, max_concurrent=10)

# Check email
response = await service.check_email("user@example.com")

print(f"Email: {response.email}")
print(f"Found on: {response.found_on}/{response.total_checked} services")

# Show accounts found
for result in response.results:
    if result.exists:
        print(f"✅ {result.name}")
```

### Check Specific Services

```python
# Only check social media
modules = ["twitter", "instagram", "facebook", "linkedin"]
response = await service.check_email(
    "user@example.com",
    modules=modules
)
```

### Bulk Email Check

```python
# Check multiple emails
emails = ["user1@example.com", "user2@example.com", "user3@example.com"]

bulk_response = await service.check_emails_bulk(
    emails=emails,
    concurrent_checks=5  # Check 5 emails at a time
)

print(f"Completed: {bulk_response.completed}/{bulk_response.total_emails}")
```

### Create Email Profile

```python
# Check email
response = await service.check_email("user@example.com")

# Create aggregated profile
profile = service.create_email_profile(response)

print(f"Total accounts: {profile.total_accounts}")
print(f"Risk score: {profile.risk_score}/100")
print(f"Social media: {profile.has_social_media}")
print(f"Professional: {profile.has_professional}")

# Show categories
for category in profile.categories:
    print(f"{category.category}: {category.found_count} accounts")
    print(f"  Services: {', '.join(category.services)}")
```

### List Available Modules

```python
# Get all available holehe modules
modules = service.get_available_modules()

print(f"Found {len(modules)} modules:")
for module in modules:
    print(f"  - {module.name} ({module.category})")
```

## Data Models

### HoleheResult

```python
{
    "name": "twitter",
    "exists": True,
    "rate_limit": False,
    "email_recovery": "ex****e@gmail.com",
    "phone_number": "0*******78",
    "others": {}
}
```

### EmailCheckResponse

```python
{
    "email": "user@example.com",
    "total_checked": 120,
    "found_on": 15,
    "rate_limited": 2,
    "results": [...],
    "duration_seconds": 45.3
}
```

### EmailProfile

```python
{
    "email": "user@example.com",
    "total_accounts": 15,
    "categories": [
        {
            "category": "social_media",
            "services": ["twitter", "instagram", "facebook"],
            "found_count": 3
        }
    ],
    "has_social_media": True,
    "has_professional": True,
    "risk_score": 75,
    "recovery_hints": ["Email: ex****e@gmail.com"]
}
```

## Service Categories

Holehe checks services across these categories:

- **Social Media**: Twitter, Instagram, Facebook, TikTok, Snapchat, etc.
- **Professional**: LinkedIn, GitHub, GitLab, Stack Overflow, Indeed
- **Gaming**: Steam, Epic Games, Twitch, Discord, Xbox, PlayStation
- **Shopping**: Amazon, eBay, Etsy, AliExpress, PayPal
- **Communication**: Skype, Telegram, WhatsApp, Viber, Discord
- **Entertainment**: Spotify, Netflix, Hulu, Disney+, YouTube

## Risk Scoring

Risk scores are calculated based on account exposure:

- **0-24**: LOW ✅ - Minimal online presence
- **25-49**: MODERATE ⚠️ - Normal online presence
- **50-74**: HIGH ⚠️ - Significant exposure
- **75-100**: CRITICAL 🔴 - Very high exposure

Formula: `risk_score = min(100, accounts_found * 5)`

## Configuration

Edit `config/holehe_osint.yaml`:

```yaml
holehe_osint:
  enabled: true
  timeout_seconds: 30
  max_concurrent_checks: 10
  retry_on_rate_limit: false
  
  # Bulk checking
  max_emails_per_bulk: 100
  concurrent_email_checks: 5
  
  # Privacy
  respect_rate_limits: true
  log_checked_emails: false
```

## Rate Limiting

Holehe may encounter rate limits:

- **Detection**: `rate_limit: true` in results
- **Handling**: Change IP or wait before retrying
- **Best Practice**: Use delays between checks
- **Mitigation**: Check specific modules instead of all

## Error Handling

```python
from src.services.holehe_osint import (
    HoleheException,
    HoleheNotInstalledException
)

try:
    response = await service.check_email("user@example.com")
except HoleheNotInstalledException:
    print("Install holehe: pip install holehe")
except HoleheException as e:
    print(f"Check failed: {e}")
```

## Privacy & Legal

### GDPR Compliance

- ✅ Only uses public "forgot password" APIs
- ✅ Does **not** alert the target email
- ✅ No personal data collection beyond what's public
- ✅ Respects rate limits
- ✅ Configurable data retention

### Legal Notice

⚠️ **Important**: This tool should only be used for:

1. **Security auditing** your own accounts
2. **OSINT research** with proper authorization
3. **Legitimate investigations** with legal authority
4. **Educational purposes**

**Always respect:**
- Privacy laws (GDPR, CCPA, etc.)
- Terms of Service of checked platforms
- Ethical OSINT practices

## Performance

### Benchmarks

- Single email (all modules): ~60-120 seconds
- Single email (10 modules): ~10-15 seconds
- Bulk (10 emails, limited modules): ~30-60 seconds
- Module check: ~0.5-2 seconds each

### Optimization

- Check specific modules instead of all 120+
- Use concurrent checks for bulk operations
- Implement caching for repeat checks
- Respect rate limits to avoid delays

## Examples

See `examples/holehe_osint_example.py` for complete examples:

```bash
python examples/holehe_osint_example.py
```

Examples include:
1. Single email check
2. Specific modules check
3. Bulk email check
4. Available modules listing
5. Risk analysis

## Testing

```bash
# Run unit tests
pytest tests/test_holehe_osint.py -v

# Run integration tests (requires holehe installed)
pytest tests/test_holehe_osint.py --run-integration

# With coverage
pytest tests/test_holehe_osint.py --cov=src/services/holehe_osint
```

## Troubleshooting

### Issue: "Holehe is not installed"

```bash
pip install holehe trio
```

### Issue: Rate limited

- Change your IP address
- Wait before retrying
- Check fewer services
- Use specific modules

### Issue: Slow checks

- Reduce timeout
- Check specific modules only
- Use concurrent checks
- Increase max_concurrent

### Issue: No results

- Verify email format
- Check internet connection
- Try different services
- Check holehe installation

## API Reference

### HoleheService

```python
class HoleheService:
    def __init__(
        self,
        timeout: int = 30,
        max_concurrent: int = 10,
        retry_on_rate_limit: bool = False
    )
    
    async def check_email(
        self,
        email: str,
        modules: Optional[List[str]] = None
    ) -> EmailCheckResponse
    
    async def check_emails_bulk(
        self,
        emails: List[str],
        modules: Optional[List[str]] = None,
        concurrent_checks: int = 5
    ) -> BulkEmailCheckResponse
    
    def create_email_profile(
        self,
        response: EmailCheckResponse
    ) -> EmailProfile
    
    def get_available_modules(self) -> List[AvailableModule]
    
    def is_available(self) -> bool
```

## Integration with IRIS

### FastAPI Endpoint Example

```python
from fastapi import APIRouter
from src.services.holehe_osint import HoleheService

router = APIRouter()
service = HoleheService()

@router.post("/api/osint/check-email")
async def check_email(email: str):
    """Check email across platforms."""
    response = await service.check_email(email)
    return response.model_dump()
```

### Background Job Example

```python
import asyncio
from src.services.holehe_osint import HoleheService

async def scheduled_email_check():
    """Scheduled email OSINT check."""
    service = HoleheService()
    
    # Load emails from database
    emails = get_emails_to_check()
    
    # Bulk check
    results = await service.check_emails_bulk(emails)
    
    # Store results
    save_results(results)

# Run daily
asyncio.create_task(scheduled_email_check())
```

## Use Cases

1. **Security Auditing**
   - Check your own email exposure
   - Identify account spread
   - Monitor account creation

2. **OSINT Research**
   - Investigate email addresses
   - Profile digital footprint
   - Identify platform presence

3. **Threat Intelligence**
   - Verify suspicious emails
   - Track account activity
   - Identify patterns

4. **Compliance**
   - Data breach response
   - Account recovery
   - Identity verification

## Limitations

1. **Rate Limits**: Some services may rate limit checks
2. **False Negatives**: Private settings may hide accounts
3. **Network Dependent**: Requires stable internet
4. **Time Consuming**: Checking 120+ services takes time
5. **API Changes**: Services may update their APIs

## Contributing

Follow IRIS coding guidelines:

- Type hints on all functions
- Async/await for I/O
- Error handling with logging
- Test coverage > 85%
- GDPR compliance
- Privacy-first design

## Support

For issues or questions:

1. Check troubleshooting section
2. Review examples
3. Check holehe documentation
4. Open GitHub issue

## Resources

- **Holehe GitHub**: https://github.com/megadose/holehe
- **Holehe PyPI**: https://pypi.org/project/holehe/
- **OSINT Framework**: https://osintframework.com/
- **GDPR Info**: https://gdpr.eu/

## License

Part of IRIS v6.0 - See main project license

Holehe itself is licensed under GNU GPL v3.0

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-06  
**Status**: Production Ready ✅
