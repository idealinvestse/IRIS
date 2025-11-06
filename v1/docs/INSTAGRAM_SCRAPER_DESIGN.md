# Instagram Scraper - Design Document

## Overview

IRIS v6.0 Instagram Scraper inspired by Apify's Instagram Scraper with enhanced image download capabilities and GDPR compliance.

## Features

### Core Capabilities

1. **Profile Scraping**
   - Extract profile metadata (username, bio, followers, following)
   - Scrape all posts from a profile
   - Download profile pictures

2. **Post Scraping**
   - Extract post metadata (caption, likes, comments count, timestamp)
   - Download post images (single images, carousels, video thumbnails)
   - Extract hashtags and mentions
   - Scrape comments

3. **Hashtag Scraping**
   - Search posts by hashtag
   - Extract hashtag statistics
   - Download top posts

4. **Location/Place Scraping**
   - Search posts by location
   - Extract place metadata

5. **Image Download**
   - Async download of high-resolution images
   - Automatic file naming (username_postid_index.jpg)
   - Storage in organized folders
   - Metadata JSON files alongside images

### Technical Architecture

```
src/services/instagram_scraper/
├── __init__.py
├── scraper.py              # Main InstagramScraper class
├── models.py               # Pydantic models for Instagram data
├── image_downloader.py     # Image download handler
├── parser.py               # HTML/JSON parser
└── config.py               # Configuration settings
```

## Data Models

### InstagramPost
```python
{
    "url": str,
    "shortcode": str,
    "type": str,  # Image, Video, Carousel
    "caption": str,
    "hashtags": List[str],
    "mentions": List[str],
    "likes_count": int,
    "comments_count": int,
    "timestamp": datetime,
    "display_url": str,
    "images": List[str],  # Additional carousel images
    "owner_username": str,
    "owner_id": str,
    "location": Optional[Dict],
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

## Implementation Strategy

### Phase 1: Core Scraper (Week 1)

1. **Setup Base Structure**
   - Create directory structure
   - Define Pydantic models
   - Setup configuration

2. **Implement InstagramScraper Class**
   ```python
   class InstagramScraper:
       async def scrape_profile(username: str) -> InstagramProfile
       async def scrape_posts(username: str, max_posts: int) -> List[InstagramPost]
       async def scrape_hashtag(hashtag: str, max_posts: int) -> List[InstagramPost]
       async def scrape_post(url: str) -> InstagramPost
   ```

3. **HTML Parser**
   - Extract data from Instagram's public JSON
   - Handle different content types
   - Error handling for missing data

### Phase 2: Image Downloader (Week 1-2)

1. **ImageDownloader Class**
   ```python
   class ImageDownloader:
       async def download_image(url: str, save_path: str) -> bool
       async def download_post_images(post: InstagramPost, folder: str) -> List[str]
       async def download_batch(urls: List[str], folder: str) -> Dict[str, bool]
   ```

2. **Features**
   - Async concurrent downloads (max 5 simultaneous)
   - Retry logic with exponential backoff
   - Progress tracking
   - File integrity checks

### Phase 3: Database Integration (Week 2)

1. **SQLAlchemy Models**
   - instagram_profiles table
   - instagram_posts table
   - instagram_images table

2. **Storage Strategy**
   - Images: `data/instagram/{username}/{postid}/`
   - Metadata: SQLite database
   - JSON exports for backup

### Phase 4: API Integration (Week 2-3)

1. **FastAPI Endpoints**
   ```python
   POST /api/instagram/scrape/profile
   POST /api/instagram/scrape/posts
   POST /api/instagram/scrape/hashtag
   GET /api/instagram/posts/{username}
   GET /api/instagram/images/{username}/{postid}
   ```

2. **Rate Limiting**
   - Max 10 requests per minute
   - Queue system for batch jobs

## Technical Specifications

### Scraping Method

**Option A: Playwright (Recommended)**
- Handles JavaScript rendering
- Bypasses some anti-bot measures
- Access to more content
- Slower but more reliable

**Option B: HTTP + BeautifulSoup**
- Faster
- No browser overhead
- Limited to public JSON data
- May be blocked easier

**Decision: Use Playwright for reliability**

### Anti-Detection Measures

1. **User-Agent Rotation**
   - Random modern browser UA strings
   - Device type variation (desktop/mobile)

2. **Request Delays**
   - Random delays between requests (2-5s)
   - Exponential backoff on errors

3. **Session Management**
   - Rotate sessions every 50 requests
   - Cookie persistence

4. **Proxy Support (Optional)**
   - Configurable proxy rotation
   - Support for residential proxies

### GDPR Compliance

1. **Only Public Data**
   - No extraction of private profiles
   - No personal data (email, phone, gender)
   - Only publicly shared content

2. **Data Retention**
   - Configurable retention policy
   - Automatic deletion after X days
   - User consent tracking

3. **Privacy Settings**
   ```yaml
   privacy:
     respect_private_profiles: true
     scrape_only_public: true
     anonymize_usernames: false  # Optional
     store_comments: false  # Comments may contain personal data
   ```

## Configuration

### config/instagram_scraper.yaml

```yaml
instagram_scraper:
  # Scraping settings
  max_posts_per_profile: 50
  max_concurrent_downloads: 5
  request_delay_min: 2
  request_delay_max: 5
  
  # Browser settings
  use_playwright: true
  headless: true
  browser_type: chromium
  
  # Storage settings
  download_images: true
  image_quality: high  # high, medium, low
  storage_path: "data/instagram"
  create_metadata_json: true
  
  # Rate limiting
  max_requests_per_minute: 10
  max_requests_per_hour: 100
  
  # Privacy & GDPR
  respect_private_profiles: true
  scrape_only_public: true
  retention_days: 30
  
  # Retry settings
  max_retries: 3
  retry_delay: 5
  backoff_multiplier: 2
```

## Usage Examples

### Basic Profile Scraping

```python
from src.services.instagram_scraper import InstagramScraper

# Initialize scraper
scraper = InstagramScraper()

# Scrape profile
profile = await scraper.scrape_profile("natgeo")
print(f"Followers: {profile.followers}")

# Scrape posts with images
posts = await scraper.scrape_posts(
    username="natgeo",
    max_posts=20,
    download_images=True
)

# Images saved to: data/instagram/natgeo/
```

### Hashtag Scraping

```python
# Scrape hashtag
posts = await scraper.scrape_hashtag(
    hashtag="nature",
    max_posts=50,
    download_images=True
)

# Filter by engagement
high_engagement = [
    post for post in posts 
    if post.likes_count > 1000
]
```

### Batch Download

```python
# Download images from multiple profiles
usernames = ["natgeo", "nasa", "bbcearth"]

for username in usernames:
    posts = await scraper.scrape_posts(
        username=username,
        max_posts=10,
        download_images=True
    )
    print(f"Downloaded {len(posts)} posts from {username}")
```

## Error Handling

### Common Scenarios

1. **Private Profile**
   ```python
   if profile.is_private:
       raise PrivateProfileException(
           f"Profile {username} is private"
       )
   ```

2. **Rate Limited**
   ```python
   if response.status_code == 429:
       retry_after = int(response.headers.get("Retry-After", 60))
       await asyncio.sleep(retry_after)
   ```

3. **Content Not Found**
   ```python
   if not posts:
       logger.warning(f"No posts found for {username}")
       return []
   ```

4. **Download Failed**
   ```python
   try:
       await download_image(url, path)
   except Exception as e:
       logger.error(f"Failed to download {url}: {e}")
       failed_downloads.append(url)
   ```

## Performance Considerations

### Benchmarks

- **Profile scraping**: ~3-5 seconds
- **Post scraping (50 posts)**: ~30-60 seconds
- **Image download (1 image)**: ~1-2 seconds
- **Batch download (10 images)**: ~5-10 seconds (concurrent)

### Optimization

1. **Async/Await**
   - All I/O operations are async
   - Concurrent image downloads

2. **Caching**
   - Cache profile data for 1 hour
   - Cache post metadata for 30 minutes

3. **Incremental Scraping**
   - Only scrape new posts (compare timestamps)
   - Skip already downloaded images

## Security

### Authentication (Optional Future Feature)

```python
# For authenticated scraping (more content access)
scraper = InstagramScraper(
    username="your_username",
    password="your_password"  # Stored encrypted
)
```

### API Keys

```env
# .env
INSTAGRAM_SCRAPER_PROXY_URL=http://proxy.example.com
INSTAGRAM_SCRAPER_USER_AGENT=Mozilla/5.0...
```

## Testing

### Test Coverage

1. **Unit Tests**
   - Test parsers with sample HTML
   - Test model validation
   - Test image downloader

2. **Integration Tests**
   - Test with real Instagram URLs
   - Test rate limiting
   - Test error handling

3. **E2E Tests**
   - Full scraping workflow
   - Database storage
   - File system checks

### Test Files

```
tests/test_instagram_scraper.py
tests/test_image_downloader.py
tests/test_instagram_parser.py
tests/fixtures/sample_instagram_data.json
```

## Monitoring & Logging

### Metrics to Track

- Total posts scraped
- Total images downloaded
- Success/failure rates
- Average response times
- Rate limit hits

### Logging

```python
logger.info(f"✅ Scraped profile: {username}")
logger.info(f"📥 Downloaded {len(images)} images")
logger.warning(f"⚠️ Rate limited, waiting {delay}s")
logger.error(f"❌ Failed to scrape {url}: {error}")
```

## Legal & Ethical Considerations

### Terms of Service

⚠️ **Important**: Instagram's Terms of Service prohibit automated scraping. This scraper should only be used for:

1. **Educational purposes**
2. **Research with proper ethics approval**
3. **Personal use with your own content**
4. **Explicitly permitted use cases**

### Best Practices

1. **Respect robots.txt**
2. **Use reasonable rate limits**
3. **Only scrape public data**
4. **Handle personal data responsibly**
5. **Provide opt-out mechanisms**

## Future Enhancements

1. **Instagram Stories** (requires authentication)
2. **Instagram Reels** scraping
3. **Video download** support
4. **Multi-language** caption detection
5. **Sentiment analysis** on comments
6. **Influencer metrics** calculation
7. **Export to CSV/Excel**
8. **Scheduled scraping** jobs

## Dependencies

```
playwright>=1.40.0
aiohttp>=3.10.5
aiofiles>=24.1.0
pillow>=10.0.0  # Image processing
pydantic>=2.9.2
sqlalchemy>=2.0.35
```

## Timeline

- **Week 1**: Core scraper + image downloader
- **Week 2**: Database integration + API endpoints
- **Week 3**: Testing + documentation
- **Week 4**: Monitoring + deployment

## Success Metrics

- ✅ Scrape 100 posts in < 2 minutes
- ✅ Download 50 images in < 1 minute
- ✅ 95%+ success rate on public profiles
- ✅ Zero GDPR violations
- ✅ 100% test coverage on critical paths

---

**Status**: Ready for implementation
**Last Updated**: 2025-11-06
**Version**: 1.0
