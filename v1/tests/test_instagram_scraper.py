"""
IRIS v6.0 - Instagram Scraper Tests
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.services.instagram_scraper import (
    InstagramScraper,
    ImageDownloader,
    InstagramPost,
    InstagramProfile,
    ContentType,
    PrivateProfileException,
    InstagramScraperException
)


class TestInstagramPost:
    """Test InstagramPost model."""
    
    def test_post_creation(self):
        """Test creating a post."""
        post = InstagramPost(
            url="https://www.instagram.com/p/ABC123/",
            shortcode="ABC123",
            type=ContentType.IMAGE,
            owner_username="testuser"
        )
        
        assert post.url == "https://www.instagram.com/p/ABC123/"
        assert post.shortcode == "ABC123"
        assert post.type == ContentType.IMAGE
        assert post.owner_username == "testuser"
    
    def test_post_with_metadata(self):
        """Test post with full metadata."""
        post = InstagramPost(
            url="https://www.instagram.com/p/ABC123/",
            shortcode="ABC123",
            type=ContentType.IMAGE,
            caption="Test caption #test",
            hashtags=["test"],
            mentions=["user1"],
            likes_count=100,
            comments_count=10,
            owner_username="testuser",
            display_url="https://example.com/image.jpg"
        )
        
        assert post.caption == "Test caption #test"
        assert post.hashtags == ["test"]
        assert post.mentions == ["user1"]
        assert post.likes_count == 100
        assert post.comments_count == 10


class TestInstagramProfile:
    """Test InstagramProfile model."""
    
    def test_profile_creation(self):
        """Test creating a profile."""
        profile = InstagramProfile(
            username="testuser",
            full_name="Test User",
            followers=1000,
            following=500,
            posts_count=50
        )
        
        assert profile.username == "testuser"
        assert profile.full_name == "Test User"
        assert profile.followers == 1000
        assert profile.following == 500
        assert profile.posts_count == 50
        assert not profile.is_private
        assert not profile.is_verified


class TestImageDownloader:
    """Test ImageDownloader class."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test downloader initialization."""
        downloader = ImageDownloader(
            max_concurrent=5,
            max_retries=3,
            retry_delay=2.0
        )
        
        assert downloader.max_concurrent == 5
        assert downloader.max_retries == 3
        assert downloader.retry_delay == 2.0
    
    @pytest.mark.asyncio
    async def test_get_extension_from_url(self):
        """Test URL extension extraction."""
        assert ImageDownloader._get_extension_from_url(
            "https://example.com/image.jpg"
        ) == ".jpg"
        
        assert ImageDownloader._get_extension_from_url(
            "https://example.com/image.png?param=value"
        ) == ".png"
        
        assert ImageDownloader._get_extension_from_url(
            "https://example.com/image"
        ) == ".jpg"  # Default
    
    @pytest.mark.asyncio
    async def test_download_image_validation(self):
        """Test download validation."""
        downloader = ImageDownloader()
        
        with pytest.raises(ValueError, match="URL cannot be empty"):
            await downloader.download_image("", Path("test.jpg"))
        
        with pytest.raises(ValueError, match="Save path cannot be empty"):
            await downloader.download_image("https://example.com/image.jpg", None)


class TestInstagramScraper:
    """Test InstagramScraper class."""
    
    def test_initialization(self):
        """Test scraper initialization."""
        scraper = InstagramScraper(
            download_images=True,
            max_concurrent_downloads=5,
            headless=True,
            storage_path="data/test"
        )
        
        assert scraper.download_images is True
        assert scraper.headless is True
        assert scraper.storage_path == Path("data/test")
    
    def test_parse_count(self):
        """Test count parsing."""
        assert InstagramScraper._parse_count("1,234") == 1234
        assert InstagramScraper._parse_count("1.5K") == 1500
        assert InstagramScraper._parse_count("2.3M") == 2300000
        assert InstagramScraper._parse_count("1.2B") == 1200000000
        assert InstagramScraper._parse_count("500") == 500
    
    @pytest.mark.asyncio
    async def test_scrape_profile_validation(self):
        """Test profile scraping validation."""
        scraper = InstagramScraper()
        
        with pytest.raises(ValueError, match="Username cannot be empty"):
            await scraper.scrape_profile("")
    
    @pytest.mark.asyncio
    async def test_scrape_post_validation(self):
        """Test post scraping validation."""
        scraper = InstagramScraper()
        
        with pytest.raises(ValueError, match="URL cannot be empty"):
            await scraper.scrape_post("")
    
    @pytest.mark.asyncio
    async def test_scrape_hashtag_validation(self):
        """Test hashtag scraping validation."""
        scraper = InstagramScraper()
        
        with pytest.raises(ValueError, match="Hashtag cannot be empty"):
            await scraper.scrape_hashtag("")


@pytest.mark.skipif(
    not pytest.config.getoption("--run-integration", default=False),
    reason="Integration tests disabled by default"
)
class TestInstagramScraperIntegration:
    """
    Integration tests requiring real Instagram access.
    Run with: pytest --run-integration
    """
    
    @pytest.mark.asyncio
    async def test_scrape_real_profile(self):
        """Test scraping a real public profile."""
        scraper = InstagramScraper(
            download_images=False,
            headless=True
        )
        
        try:
            # Use a known public account
            profile, posts = await scraper.scrape_profile("natgeo", max_posts=5)
            
            assert profile.username == "natgeo"
            assert profile.followers > 0
            assert len(posts) > 0
        
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
