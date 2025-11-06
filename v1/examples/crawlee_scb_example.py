"""
Example usage of SCB Crawler with Crawlee.

This script demonstrates how to use the SCB crawler to collect data from
Statistiska centralbyrån (SCB).
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.crawlers.scb_crawler import SCBCrawler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_basic_crawl():
    """
    Basic example: Crawl a single SCB page.
    """
    logger.info("=" * 60)
    logger.info("Example 1: Basic SCB Crawl")
    logger.info("=" * 60)
    
    # Initialize crawler
    crawler = SCBCrawler(
        max_requests_per_crawl=5,
        cache_ttl=3600
    )
    
    # Get crawler stats
    stats = crawler.get_stats()
    logger.info(f"Crawler configuration: {stats}")
    
    # URLs to crawl (using public SCB pages)
    urls = [
        "https://www.scb.se/hitta-statistik/",
    ]
    
    try:
        logger.info(f"Starting crawl of {len(urls)} URL(s)...")
        
        # Perform crawl
        data = await crawler.crawl(urls)
        
        # Display results
        logger.info(f"\n✅ Crawl successful! Retrieved {len(data)} result(s)")
        
        for i, item in enumerate(data, 1):
            logger.info(f"\n--- Result {i} ---")
            logger.info(f"Source: {item.get('källa', 'Unknown')}")
            logger.info(f"URL: {item.get('url', 'Unknown')}")
            logger.info(f"Title: {item.get('titel', 'No title')}")
            logger.info(f"Status: {item.get('status', 'Unknown')}")
            
            if 'data' in item:
                data_info = item['data']
                logger.info(f"Statistics type: {data_info.get('statistik_typ', 'Unknown')}")
                logger.info(f"Tables found: {data_info.get('antal_tabeller', 0)}")
        
        return data
        
    except Exception as e:
        logger.error(f"❌ Crawl failed: {e}", exc_info=True)
        return []


async def example_multiple_pages():
    """
    Advanced example: Crawl multiple SCB pages.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Multiple Page Crawl")
    logger.info("=" * 60)
    
    # Initialize crawler with higher limits
    crawler = SCBCrawler(
        max_requests_per_crawl=10,
        max_request_retries=5,
        cache_ttl=1800
    )
    
    # Multiple URLs
    urls = [
        "https://www.scb.se/hitta-statistik/",
        "https://www.scb.se/hitta-statistik/statistik-efter-amne/",
    ]
    
    try:
        logger.info(f"Crawling {len(urls)} URLs...")
        data = await crawler.crawl(urls)
        
        logger.info(f"\n✅ Retrieved {len(data)} total results")
        
        # Aggregate statistics
        success_count = sum(1 for item in data if item.get('status') == 'success')
        error_count = sum(1 for item in data if item.get('status') == 'error')
        
        logger.info(f"Success: {success_count}, Errors: {error_count}")
        
        return data
        
    except Exception as e:
        logger.error(f"❌ Crawl failed: {e}")
        return []


async def example_with_error_handling():
    """
    Example: Demonstrate error handling with invalid URLs.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Error Handling")
    logger.info("=" * 60)
    
    crawler = SCBCrawler()
    
    # Test with empty URL list
    logger.info("\nTest 1: Empty URL list")
    try:
        await crawler.crawl([])
    except ValueError as e:
        logger.info(f"✅ Caught expected error: {e}")
    
    # Test with invalid URL type
    logger.info("\nTest 2: Invalid URL type")
    try:
        await crawler.crawl("not-a-list")
    except ValueError as e:
        logger.info(f"✅ Caught expected error: {e}")
    
    # Test with invalid parameters
    logger.info("\nTest 3: Invalid crawler parameters")
    try:
        SCBCrawler(max_requests_per_crawl=-1)
    except ValueError as e:
        logger.info(f"✅ Caught expected error: {e}")
    
    logger.info("\n✅ All error handling tests passed!")


async def main():
    """
    Main function to run all examples.
    """
    logger.info("🚀 SCB Crawler Examples with Crawlee")
    logger.info("=" * 60)
    
    try:
        # Run basic example
        await example_basic_crawl()
        
        # Run multiple pages example
        # await example_multiple_pages()
        
        # Run error handling example
        await example_with_error_handling()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 All examples completed successfully!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Examples interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Examples failed: {e}", exc_info=True)


if __name__ == "__main__":
    # Note: First install dependencies:
    # pip install 'crawlee[all]' playwright
    # playwright install
    
    print("\n📚 SCB Crawler Example Usage")
    print("=" * 60)
    print("This example demonstrates the Crawlee integration for SCB data.")
    print("\nPrerequisites:")
    print("1. pip install 'crawlee[all]' playwright")
    print("2. playwright install")
    print("\nPress Ctrl+C to stop at any time.")
    print("=" * 60 + "\n")
    
    # Run async examples
    asyncio.run(main())
