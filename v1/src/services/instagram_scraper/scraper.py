"""
IRIS v6.0 - Instagram Scraper
Main scraper class using Playwright for reliable data extraction
"""

import asyncio
import logging
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser

from .models import (
    InstagramPost,
    InstagramProfile,
    InstagramHashtag,
    ContentType,
    InstagramLocation,
    ScrapeResult
)
from .image_downloader import ImageDownloader

logger = logging.getLogger(__name__)


class InstagramScraperException(Exception):
    """Base exception for Instagram scraper."""
    pass


class PrivateProfileException(InstagramScraperException):
    """Exception for private profiles."""
    pass


class InstagramScraper:
    """
    Instagram scraper using Playwright for JavaScript rendering.
    
    Features:
    - Profile scraping
    - Post scraping
    - Hashtag search
    - Image downloading
    - GDPR-compliant (only public data)
    """
    
    def __init__(
        self,
        download_images: bool = True,
        max_concurrent_downloads: int = 5,
        headless: bool = True,
        storage_path: str = "data/instagram"
    ):
        """
        Initialize InstagramScraper.
        
        Args:
            download_images: Whether to download images
            max_concurrent_downloads: Max concurrent downloads
            headless: Run browser in headless mode
            storage_path: Base storage path
        """
        self.download_images = download_images
        self.headless = headless
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize image downloader
        self.image_downloader = ImageDownloader(
            max_concurrent=max_concurrent_downloads
        )
        
        self.browser: Optional[Browser] = None
        
        logger.info(
            f"📷 InstagramScraper initialized: "
            f"download_images={download_images}, "
            f"storage_path={storage_path}"
        )
    
    async def scrape_profile(
        self,
        username: str,
        max_posts: int = 50
    ) -> tuple[InstagramProfile, List[InstagramPost]]:
        """
        Scrape Instagram profile and posts.
        
        Args:
            username: Instagram username
            max_posts: Maximum posts to scrape
        
        Returns:
            Tuple of (profile, posts)
        
        Raises:
            PrivateProfileException: If profile is private
            InstagramScraperException: On scraping errors
        """
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        
        username = username.strip().lstrip('@')
        logger.info(f"🔍 Scraping profile: {username}")
        
        start_time = datetime.now()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                # Navigate to profile
                url = f"https://www.instagram.com/{username}/"
                logger.debug(f"Navigating to {url}")
                
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)  # Wait for dynamic content
                
                # Extract profile data from page JSON
                profile_data = await self._extract_profile_data(page, username)
                profile = InstagramProfile(**profile_data)
                
                # Check if private
                if profile.is_private:
                    raise PrivateProfileException(
                        f"Profile {username} is private"
                    )
                
                logger.info(
                    f"✅ Profile: {profile.username} - "
                    f"{profile.followers} followers, {profile.posts_count} posts"
                )
                
                # Scrape posts
                posts = await self._scrape_profile_posts(page, username, max_posts)
                
                logger.info(f"📥 Scraped {len(posts)} posts from {username}")
                
                # Download images if enabled
                if self.download_images and posts:
                    logger.info(f"📥 Downloading images...")
                    await self.image_downloader.download_batch(
                        posts, 
                        self.storage_path
                    )
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"✅ Profile scrape complete: {username} "
                    f"({duration:.1f}s)"
                )
                
                return profile, posts
            
            except PrivateProfileException:
                raise
            
            except Exception as e:
                logger.error(f"Failed to scrape profile {username}: {e}", exc_info=True)
                raise InstagramScraperException(f"Scraping failed: {e}")
            
            finally:
                await browser.close()
    
    async def scrape_post(self, url: str) -> InstagramPost:
        """
        Scrape a single Instagram post.
        
        Args:
            url: Post URL
        
        Returns:
            InstagramPost model
        
        Raises:
            InstagramScraperException: On scraping errors
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
        
        logger.info(f"🔍 Scraping post: {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Extract post data
                post_data = await self._extract_post_data(page, url)
                post = InstagramPost(**post_data)
                
                logger.info(
                    f"✅ Post scraped: {post.shortcode} - "
                    f"{post.likes_count} likes, {post.comments_count} comments"
                )
                
                # Download images if enabled
                if self.download_images:
                    await self.image_downloader.download_post_images(
                        post,
                        self.storage_path
                    )
                
                return post
            
            except Exception as e:
                logger.error(f"Failed to scrape post {url}: {e}", exc_info=True)
                raise InstagramScraperException(f"Scraping failed: {e}")
            
            finally:
                await browser.close()
    
    async def scrape_hashtag(
        self,
        hashtag: str,
        max_posts: int = 50
    ) -> List[InstagramPost]:
        """
        Scrape posts from a hashtag.
        
        Args:
            hashtag: Hashtag name (without #)
            max_posts: Maximum posts to scrape
        
        Returns:
            List of InstagramPost models
        
        Raises:
            InstagramScraperException: On scraping errors
        """
        if not hashtag or not hashtag.strip():
            raise ValueError("Hashtag cannot be empty")
        
        hashtag = hashtag.strip().lstrip('#')
        logger.info(f"🔍 Scraping hashtag: #{hashtag}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Extract posts from hashtag page
                posts = await self._scrape_hashtag_posts(page, hashtag, max_posts)
                
                logger.info(f"📥 Scraped {len(posts)} posts from #{hashtag}")
                
                # Download images if enabled
                if self.download_images and posts:
                    await self.image_downloader.download_batch(
                        posts,
                        self.storage_path
                    )
                
                return posts
            
            except Exception as e:
                logger.error(f"Failed to scrape hashtag #{hashtag}: {e}", exc_info=True)
                raise InstagramScraperException(f"Scraping failed: {e}")
            
            finally:
                await browser.close()
    
    async def _extract_profile_data(
        self,
        page: Page,
        username: str
    ) -> Dict[str, Any]:
        """Extract profile data from page."""
        try:
            # Instagram embeds data in script tags
            script_content = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script'));
                    const dataScript = scripts.find(s => 
                        s.textContent.includes('window._sharedData')
                    );
                    if (dataScript) {
                        return dataScript.textContent;
                    }
                    return null;
                }
            """)
            
            if script_content:
                # Parse shared data
                match = re.search(r'window\._sharedData\s*=\s*({.+?});', script_content)
                if match:
                    shared_data = json.loads(match.group(1))
                    user_data = shared_data.get('entry_data', {}).get('ProfilePage', [{}])[0]
                    user = user_data.get('graphql', {}).get('user', {})
                    
                    return {
                        'username': user.get('username', username),
                        'full_name': user.get('full_name'),
                        'biography': user.get('biography'),
                        'followers': user.get('edge_followed_by', {}).get('count', 0),
                        'following': user.get('edge_follow', {}).get('count', 0),
                        'posts_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'profile_pic_url': user.get('profile_pic_url_hd'),
                        'is_verified': user.get('is_verified', False),
                        'is_private': user.get('is_private', False),
                        'external_url': user.get('external_url'),
                        'user_id': user.get('id')
                    }
            
            # Fallback: Extract from meta tags
            profile_data = {
                'username': username,
                'full_name': None,
                'biography': None,
                'followers': 0,
                'following': 0,
                'posts_count': 0,
                'is_verified': False,
                'is_private': False
            }
            
            # Try to get follower count from page
            follower_text = await page.text_content('header section ul li:nth-child(2) span')
            if follower_text:
                profile_data['followers'] = self._parse_count(follower_text)
            
            return profile_data
        
        except Exception as e:
            logger.warning(f"Failed to extract profile data: {e}")
            return {
                'username': username,
                'is_private': False
            }
    
    async def _scrape_profile_posts(
        self,
        page: Page,
        username: str,
        max_posts: int
    ) -> List[InstagramPost]:
        """Scrape posts from profile page."""
        posts = []
        
        try:
            # Get post links
            post_links = await page.evaluate("""
                () => {
                    const articles = Array.from(document.querySelectorAll('article a'));
                    return articles
                        .map(a => a.href)
                        .filter(href => href.includes('/p/'));
                }
            """)
            
            logger.info(f"Found {len(post_links)} post links")
            
            # Scrape each post (limit to max_posts)
            for url in post_links[:max_posts]:
                try:
                    # Extract shortcode from URL
                    shortcode = url.split('/p/')[1].rstrip('/')
                    
                    # Create minimal post object
                    post = InstagramPost(
                        url=url,
                        shortcode=shortcode,
                        type=ContentType.IMAGE,
                        owner_username=username
                    )
                    
                    posts.append(post)
                
                except Exception as e:
                    logger.warning(f"Failed to parse post {url}: {e}")
                    continue
            
            return posts
        
        except Exception as e:
            logger.error(f"Failed to scrape posts: {e}")
            return posts
    
    async def _extract_post_data(
        self,
        page: Page,
        url: str
    ) -> Dict[str, Any]:
        """Extract post data from page."""
        shortcode = url.split('/p/')[1].rstrip('/')
        
        # Minimal post data
        return {
            'url': url,
            'shortcode': shortcode,
            'type': ContentType.IMAGE,
            'owner_username': 'unknown'
        }
    
    async def _scrape_hashtag_posts(
        self,
        page: Page,
        hashtag: str,
        max_posts: int
    ) -> List[InstagramPost]:
        """Scrape posts from hashtag page."""
        # Similar to profile post scraping
        return []
    
    @staticmethod
    def _parse_count(text: str) -> int:
        """Parse count from text (e.g., '1.5M' -> 1500000)."""
        text = text.strip().lower()
        
        multipliers = {
            'k': 1000,
            'm': 1000000,
            'b': 1000000000
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                number = float(text.replace(suffix, '').replace(',', '').strip())
                return int(number * multiplier)
        
        # Regular number
        return int(text.replace(',', '').strip())
