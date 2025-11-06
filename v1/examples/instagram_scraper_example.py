"""
IRIS v6.0 - Instagram Scraper Example
Demonstrates how to use the Instagram scraper
"""

import asyncio
import logging
from pathlib import Path

from src.services.instagram_scraper import (
    InstagramScraper,
    PrivateProfileException,
    InstagramScraperException
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_scrape_profile():
    """Example: Scrape an Instagram profile."""
    logger.info("=" * 60)
    logger.info("Example 1: Scrape Instagram Profile")
    logger.info("=" * 60)
    
    # Initialize scraper
    scraper = InstagramScraper(
        download_images=True,
        max_concurrent_downloads=5,
        headless=True,
        storage_path="data/instagram"
    )
    
    try:
        # Scrape profile (use a public account)
        username = "natgeo"  # National Geographic (public)
        
        logger.info(f"Scraping profile: {username}")
        profile, posts = await scraper.scrape_profile(
            username=username,
            max_posts=10  # Limit to 10 posts for demo
        )
        
        # Display results
        logger.info("\n📊 Profile Information:")
        logger.info(f"  Username: @{profile.username}")
        logger.info(f"  Full Name: {profile.full_name}")
        logger.info(f"  Followers: {profile.followers:,}")
        logger.info(f"  Following: {profile.following:,}")
        logger.info(f"  Posts: {profile.posts_count:,}")
        logger.info(f"  Verified: {profile.is_verified}")
        
        logger.info(f"\n📸 Scraped {len(posts)} posts:")
        for idx, post in enumerate(posts[:5], 1):  # Show first 5
            logger.info(f"\n  Post {idx}:")
            logger.info(f"    URL: {post.url}")
            logger.info(f"    Type: {post.type}")
            logger.info(f"    Likes: {post.likes_count:,}")
            logger.info(f"    Comments: {post.comments_count:,}")
            if post.caption:
                caption_preview = post.caption[:100] + "..." if len(post.caption) > 100 else post.caption
                logger.info(f"    Caption: {caption_preview}")
        
        logger.info(f"\n✅ Images saved to: data/instagram/{username}/")
    
    except PrivateProfileException as e:
        logger.error(f"❌ Profile is private: {e}")
    
    except InstagramScraperException as e:
        logger.error(f"❌ Scraping failed: {e}")
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)


async def example_scrape_post():
    """Example: Scrape a single post."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Scrape Single Post")
    logger.info("=" * 60)
    
    scraper = InstagramScraper(
        download_images=True,
        storage_path="data/instagram"
    )
    
    try:
        # Example post URL (use a real public post)
        post_url = "https://www.instagram.com/p/ABC123/"
        
        logger.info(f"Scraping post: {post_url}")
        post = await scraper.scrape_post(post_url)
        
        logger.info("\n📸 Post Information:")
        logger.info(f"  Shortcode: {post.shortcode}")
        logger.info(f"  Owner: @{post.owner_username}")
        logger.info(f"  Type: {post.type}")
        logger.info(f"  Likes: {post.likes_count:,}")
        logger.info(f"  Comments: {post.comments_count:,}")
        
        if post.caption:
            logger.info(f"  Caption: {post.caption[:200]}...")
        
        if post.hashtags:
            logger.info(f"  Hashtags: {', '.join(f'#{tag}' for tag in post.hashtags)}")
        
        logger.info(f"\n✅ Images saved to: data/instagram/{post.owner_username}/{post.shortcode}/")
    
    except InstagramScraperException as e:
        logger.error(f"❌ Scraping failed: {e}")


async def example_scrape_hashtag():
    """Example: Scrape posts from a hashtag."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Scrape Hashtag")
    logger.info("=" * 60)
    
    scraper = InstagramScraper(
        download_images=True,
        storage_path="data/instagram"
    )
    
    try:
        hashtag = "nature"
        
        logger.info(f"Scraping hashtag: #{hashtag}")
        posts = await scraper.scrape_hashtag(
            hashtag=hashtag,
            max_posts=20
        )
        
        logger.info(f"\n📊 Scraped {len(posts)} posts from #{hashtag}")
        
        # Show top posts by engagement
        sorted_posts = sorted(posts, key=lambda p: p.likes_count, reverse=True)
        
        logger.info("\n🔥 Top posts by likes:")
        for idx, post in enumerate(sorted_posts[:5], 1):
            logger.info(f"\n  {idx}. @{post.owner_username}")
            logger.info(f"     Likes: {post.likes_count:,}")
            logger.info(f"     Comments: {post.comments_count:,}")
            logger.info(f"     URL: {post.url}")
        
        logger.info(f"\n✅ Images saved to: data/instagram/")
    
    except InstagramScraperException as e:
        logger.error(f"❌ Scraping failed: {e}")


async def example_batch_download():
    """Example: Batch download from multiple profiles."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Batch Download")
    logger.info("=" * 60)
    
    scraper = InstagramScraper(
        download_images=True,
        max_concurrent_downloads=5,
        storage_path="data/instagram"
    )
    
    # List of profiles to scrape
    usernames = [
        "natgeo",
        "nasa",
        "bbcearth"
    ]
    
    total_posts = 0
    
    for username in usernames:
        try:
            logger.info(f"\n📥 Scraping: @{username}")
            profile, posts = await scraper.scrape_profile(
                username=username,
                max_posts=5  # Limit to 5 posts each
            )
            
            total_posts += len(posts)
            logger.info(f"  ✅ Scraped {len(posts)} posts from @{username}")
        
        except Exception as e:
            logger.error(f"  ❌ Failed to scrape @{username}: {e}")
    
    logger.info(f"\n✅ Batch complete: {total_posts} total posts scraped")


async def main():
    """Run all examples."""
    logger.info("🚀 Instagram Scraper Examples")
    logger.info("⚠️  Note: These are examples. Use responsibly and respect ToS.\n")
    
    # Run examples
    # await example_scrape_profile()
    # await example_scrape_post()
    # await example_scrape_hashtag()
    # await example_batch_download()
    
    logger.info("\n" + "=" * 60)
    logger.info("💡 Tips:")
    logger.info("  - Uncomment examples above to run")
    logger.info("  - Replace usernames/URLs with real public accounts")
    logger.info("  - Check data/instagram/ for downloaded content")
    logger.info("  - Respect rate limits and Instagram ToS")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
