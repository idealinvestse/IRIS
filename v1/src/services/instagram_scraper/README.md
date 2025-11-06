# Instagram Scraper for IRIS v6.0

A robust, async Instagram scraper with image download capabilities, inspired by Apify's Instagram Scraper.

## Features

- ✅ **Profile Scraping** - Extract profile metadata and posts
- ✅ **Post Scraping** - Scrape individual posts with metadata
- ✅ **Hashtag Search** - Find posts by hashtag
- ✅ **Image Download** - Concurrent async image downloads
- ✅ **GDPR Compliant** - Only public data, no PII
- ✅ **Retry Logic** - Exponential backoff on failures
- ✅ **Progress Tracking** - Monitor download progress
- ✅ **Metadata Storage** - JSON files with post metadata

## Architecture

```
src/services/instagram_scraper/
├── __init__.py           # Module exports
├── scraper.py            # Main InstagramScraper class
├── models.py             # Pydantic data models
├── image_downloader.py   # Async image downloader
└── README.md             # This file
```

## Installation

### Requirements

```bash
# Install Playwright
pip install playwright>=1.40.0
python -m playwright install chromium

# Already included in IRIS requirements.txt:
# - aiohttp>=3.10.5
# - aiofiles>=24.1.0
# - pydantic>=2.9.2
```

### Configuration

Edit `config/instagram_scraper.yaml`:

```yaml
instagram_scraper:
  max_posts_per_profile: 50
  max_concurrent_downloads: 5
  download_images: true
  storage_path: "data/instagram"
  headless: true
  respect_private_profiles: true
```

## Usage

### Basic Profile Scraping

```python
from src.services.instagram_scraper import InstagramScraper

# Initialize scraper
scraper = InstagramScraper(
    download_images=True,
    storage_path="data/instagram"
)

# Scrape profile
profile, posts = await scraper.scrape_profile(
    username="natgeo",
    max_posts=20
)

print(f"Username: {profile.username}")
print(f"Followers: {profile.followers:,}")
print(f"Scraped {len(posts)} posts")
```

### Single Post Scraping

```python
# Scrape single post
post = await scraper.scrape_post(
    "https://www.instagram.com/p/ABC123/"
)

print(f"Likes: {post.likes_count:,}")
print(f"Comments: {post.comments_count:,}")
print(f"Caption: {post.caption}")
```

### Hashtag Search

```python
# Search by hashtag
posts = await scraper.scrape_hashtag(
    hashtag="nature",
    max_posts=50
)

# Filter high engagement posts
top_posts = [p for p in posts if p.likes_count > 10000]
```

### Batch Download

```python
# Download from multiple profiles
usernames = ["natgeo", "nasa", "bbcearth"]

for username in usernames:
    profile, posts = await scraper.scrape_profile(
        username=username,
        max_posts=10
    )
    print(f"Downloaded {len(posts)} posts from @{username}")
```

## Data Models

### InstagramPost

```python
{
    "url": str,
    "shortcode": str,
    "type": "Image" | "Video" | "Carousel" | "Reel",
    "caption": str,
    "hashtags": List[str],
    "mentions": List[str],
    "likes_count": int,
    "comments_count": int,
    "timestamp": datetime,
    "display_url": str,
    "images": List[str],
    "owner_username": str,
    "location": Optional[dict],
    "is_sponsored": bool
}
```

### InstagramProfile

```python
{
    "username": str,
    "full_name": str,
    "biography": str,
    "followers": int,
    "following": int,
    "posts_count": int,
    "profile_pic_url": str,
    "is_verified": bool,
    "is_private": bool
}
```

## Storage Structure

```
data/instagram/
├── natgeo/
│   ├── ABC123/
│   │   ├── ABC123_1.jpg
│   │   ├── ABC123_2.jpg
│   │   └── ABC123_metadata.json
│   └── DEF456/
│       ├── DEF456_1.jpg
│       └── DEF456_metadata.json
└── nasa/
    └── ...
```

## Error Handling

```python
from src.services.instagram_scraper import (
    InstagramScraperException,
    PrivateProfileException
)

try:
    profile, posts = await scraper.scrape_profile("username")
except PrivateProfileException:
    print("Profile is private")
except InstagramScraperException as e:
    print(f"Scraping failed: {e}")
```

## Rate Limiting

The scraper includes built-in rate limiting:

- Max 10 requests per minute
- Max 100 requests per hour
- Random delays between requests (2-5 seconds)
- Exponential backoff on errors

## GDPR Compliance

This scraper is designed to be GDPR-compliant:

- ✅ Only scrapes **public** data
- ✅ Respects private profile settings
- ✅ No extraction of personal data (email, phone, location)
- ✅ No storage of sensitive information
- ✅ Configurable data retention
- ✅ Comments scraping disabled by default (may contain PII)

## Legal Notice

⚠️ **Important**: Instagram's Terms of Service prohibit automated scraping. This tool should only be used for:

1. **Educational purposes**
2. **Research with proper ethics approval**
3. **Personal use with your own content**
4. **Explicitly permitted use cases**

**Use responsibly and respect Instagram's Terms of Service.**

## Performance

### Benchmarks

- Profile scraping: ~3-5 seconds
- Post scraping (50 posts): ~30-60 seconds
- Image download (1 image): ~1-2 seconds
- Batch download (10 images): ~5-10 seconds (concurrent)

### Optimization

- Async/await for all I/O operations
- Concurrent image downloads (max 5 simultaneous)
- Connection pooling
- Request caching

## Testing

```bash
# Run unit tests
pytest tests/test_instagram_scraper.py -v

# Run with coverage
pytest tests/test_instagram_scraper.py --cov=src/services/instagram_scraper

# Run integration tests (requires internet)
pytest tests/test_instagram_scraper.py --run-integration
```

## Troubleshooting

### Issue: "Playwright not installed"

```bash
python -m playwright install chromium
```

### Issue: "Timeout errors"

Increase timeout in configuration:

```yaml
timeout_seconds: 60  # Increase from 30
```

### Issue: "Rate limited"

Increase delays:

```yaml
request_delay_min: 5
request_delay_max: 10
```

### Issue: "No posts found"

The profile might be:
- Private (check `is_private`)
- Has no posts
- Blocked by Instagram

## Examples

See `examples/instagram_scraper_example.py` for complete examples:

```bash
python examples/instagram_scraper_example.py
```

## API Reference

### InstagramScraper

```python
class InstagramScraper:
    def __init__(
        self,
        download_images: bool = True,
        max_concurrent_downloads: int = 5,
        headless: bool = True,
        storage_path: str = "data/instagram"
    )
    
    async def scrape_profile(
        self,
        username: str,
        max_posts: int = 50
    ) -> tuple[InstagramProfile, List[InstagramPost]]
    
    async def scrape_post(
        self,
        url: str
    ) -> InstagramPost
    
    async def scrape_hashtag(
        self,
        hashtag: str,
        max_posts: int = 50
    ) -> List[InstagramPost]
```

### ImageDownloader

```python
class ImageDownloader:
    def __init__(
        self,
        max_concurrent: int = 5,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        timeout: int = 30
    )
    
    async def download_image(
        self,
        url: str,
        save_path: Path
    ) -> Tuple[bool, Optional[str]]
    
    async def download_post_images(
        self,
        post: InstagramPost,
        base_folder: Path
    ) -> List[str]
    
    async def download_batch(
        self,
        posts: List[InstagramPost],
        base_folder: Path,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, List[str]]
```

## Contributing

Follow IRIS coding guidelines:

- Type hints on all functions
- Async/await for I/O
- Error handling with try/except
- Logging at appropriate levels
- Test coverage > 85%
- GDPR compliance

## Roadmap

- [ ] Instagram Stories support
- [ ] Instagram Reels scraping
- [ ] Video download support
- [ ] Multi-language caption detection
- [ ] Sentiment analysis on captions
- [ ] Influencer metrics calculation
- [ ] Export to CSV/Excel
- [ ] Scheduled scraping jobs
- [ ] Webhook notifications

## Support

For issues or questions:

1. Check troubleshooting section
2. Review examples
3. Check logs in `data/logs/`
4. Open GitHub issue

## License

Part of IRIS v6.0 - See main project license

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-06  
**Status**: Production Ready ✅
