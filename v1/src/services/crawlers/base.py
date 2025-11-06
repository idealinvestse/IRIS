"""
Base crawler for Swedish data sources using Crawlee.

This module provides an abstract base class for all Swedish data source crawlers,
implementing common functionality like rate limiting, error handling, and caching.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import Dataset

logger = logging.getLogger(__name__)


class BaseSwedishCrawler(ABC):
    """
    Abstract base class for Swedish data source crawlers.
    
    Provides common functionality for all Swedish data crawlers including:
    - Automatic retries with exponential backoff
    - Request queuing and deduplication
    - Session management for anti-blocking
    - Data persistence and caching
    - Error handling and logging
    
    All Swedish data source crawlers should inherit from this class and implement
    the abstract methods for source-specific behavior.
    
    Attributes:
        max_requests_per_crawl: Maximum requests allowed per crawl session
        max_request_retries: Maximum retry attempts for failed requests
        cache_ttl: Cache time-to-live in seconds
        crawler: The Crawlee crawler instance
    
    Example:
        >>> class MySw

edishCrawler(BaseSwedishCrawler):
        ...     def _create_crawler(self):
        ...         return BeautifulSoupCrawler()
        ...     
        ...     async def extract_data(self, context):
        ...         return {"data": "extracted"}
        >>> 
        >>> crawler = MySwedishCrawler()
        >>> data = await crawler.crawl(["https://example.se"])
    """
    
    def __init__(
        self,
        max_requests_per_crawl: int = 100,
        max_request_retries: int = 3,
        cache_ttl: int = 3600,
    ) -> None:
        """
        Initialize base Swedish crawler.
        
        Args:
            max_requests_per_crawl: Maximum requests per crawl session (default: 100)
            max_request_retries: Maximum retry attempts (default: 3)
            cache_ttl: Cache time-to-live in seconds (default: 3600)
        
        Raises:
            ValueError: If parameters are invalid
        """
        if max_requests_per_crawl <= 0:
            raise ValueError("max_requests_per_crawl must be positive")
        if max_request_retries < 0:
            raise ValueError("max_request_retries cannot be negative")
        if cache_ttl < 0:
            raise ValueError("cache_ttl cannot be negative")
        
        self.max_requests_per_crawl = max_requests_per_crawl
        self.max_request_retries = max_request_retries
        self.cache_ttl = cache_ttl
        
        # Initialize crawler
        self.crawler = self._create_crawler()
        
        # Setup request router
        self._setup_router()
        
        logger.info(
            f"✅ Initialized {self.__class__.__name__} "
            f"(max_requests={max_requests_per_crawl}, "
            f"retries={max_request_retries}, cache_ttl={cache_ttl}s)"
        )
    
    @abstractmethod
    def _create_crawler(self) -> BeautifulSoupCrawler:
        """
        Create and configure the Crawlee crawler.
        
        This method must be implemented by subclasses to create a crawler
        specific to their data source requirements.
        
        Returns:
            Configured Crawlee crawler instance
        
        Example:
            >>> def _create_crawler(self):
            ...     return BeautifulSoupCrawler(
            ...         max_requests_per_crawl=self.max_requests_per_crawl
            ...     )
        """
        pass
    
    @abstractmethod
    def _setup_router(self) -> None:
        """
        Setup request routing and handlers.
        
        This method must be implemented by subclasses to configure how
        requests should be routed and handled.
        
        Example:
            >>> def _setup_router(self):
            ...     @self.crawler.router.default_handler
            ...     async def handler(context):
            ...         data = await self.extract_data(context)
            ...         await context.push_data(data)
        """
        pass
    
    @abstractmethod
    async def extract_data(
        self,
        context: BeautifulSoupCrawlingContext
    ) -> Dict[str, Any]:
        """
        Extract data from crawling context.
        
        This method must be implemented by subclasses to extract source-specific
        data from the crawled page.
        
        Args:
            context: Crawlee crawling context containing page data
        
        Returns:
            Dictionary containing extracted data
        
        Raises:
            ValueError: If context is invalid
            Exception: If extraction fails
        
        Example:
            >>> async def extract_data(self, context):
            ...     soup = context.soup
            ...     return {
            ...         "källa": "SCB",
            ...         "titel": soup.title.string,
            ...         "data": {}
            ...     }
        """
        pass
    
    async def crawl(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Crawl URLs and extract data.
        
        Main entry point for crawling. Handles the complete crawl lifecycle:
        1. Validates input URLs
        2. Runs the crawler
        3. Retrieves extracted data from storage
        4. Returns processed results
        
        Args:
            urls: List of URLs to crawl
        
        Returns:
            List of extracted data dictionaries, one per successful crawl
        
        Raises:
            ValueError: If URLs list is empty or invalid
            Exception: If crawling fails critically
        
        Example:
            >>> urls = ["https://scb.se/page1", "https://scb.se/page2"]
            >>> data = await crawler.crawl(urls)
            >>> print(len(data))  # Number of successfully crawled pages
        """
        if not urls:
            raise ValueError("URLs list cannot be empty")
        
        if not isinstance(urls, list):
            raise ValueError("URLs must be a list")
        
        # Validate URLs
        valid_urls = [url for url in urls if url and isinstance(url, str)]
        if not valid_urls:
            raise ValueError("No valid URLs provided")
        
        try:
            logger.info(f"🕷️ Starting crawl of {len(valid_urls)} URLs")
            
            # Run crawler
            await self.crawler.run(valid_urls)
            
            # Get dataset with results
            dataset = await Dataset.open()
            
            # Export data
            data_result = await dataset.get_data()
            
            # Convert to list
            extracted_data = [item for item in data_result.items]
            
            logger.info(
                f"✅ Crawl complete: {len(extracted_data)} items extracted "
                f"from {len(valid_urls)} URLs"
            )
            
            return extracted_data
            
        except Exception as e:
            logger.error(
                f"❌ Crawl failed for {self.__class__.__name__}: {e}",
                exc_info=True
            )
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get crawler statistics.
        
        Returns:
            Dictionary with crawler statistics and configuration
        
        Example:
            >>> stats = crawler.get_stats()
            >>> print(stats['max_requests'])
        """
        return {
            "crawler_name": self.__class__.__name__,
            "max_requests": self.max_requests_per_crawl,
            "max_retries": self.max_request_retries,
            "cache_ttl": self.cache_ttl,
        }
