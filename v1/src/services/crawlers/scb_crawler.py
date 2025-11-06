"""
SCB (Statistiska centralbyrån) data crawler using Crawlee.

This module provides a robust crawler for extracting statistical data from
Statistiska centralbyrån (SCB), Sweden's official statistics agency.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from .base import BaseSwedishCrawler

logger = logging.getLogger(__name__)


class SCBCrawler(BaseSwedishCrawler):
    """
    Crawler for SCB (Statistiska centralbyrån) statistical data.
    
    This crawler extracts official statistics from SCB's public API and web pages.
    It handles:
    - Population statistics
    - Economic indicators
    - Labor market data
    - Other official Swedish statistics
    
    Attributes:
        source_name: Name of the data source ("SCB")
        base_url: Base URL for SCB API
    
    Example:
        >>> crawler = SCBCrawler(max_requests_per_crawl=50)
        >>> urls = ["https://api.scb.se/OV0104/v1/doris/sv/ssd/..."]
        >>> data = await crawler.crawl(urls)
        >>> print(data[0]['källa'])  # "SCB"
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize SCB crawler.
        
        Args:
            **kwargs: Additional arguments passed to BaseSwedishCrawler
        
        Example:
            >>> crawler = SCBCrawler(
            ...     max_requests_per_crawl=50,
            ...     cache_ttl=3600
            ... )
        """
        self.source_name = "SCB"
        self.base_url = "https://api.scb.se"
        
        super().__init__(**kwargs)
        
        logger.info(f"✅ {self.source_name} Crawler initialized")
    
    def _create_crawler(self) -> BeautifulSoupCrawler:
        """
        Create SCB-specific crawler.
        
        Configures a BeautifulSoupCrawler optimized for SCB's API structure
        with appropriate timeouts and retry settings.
        
        Returns:
            Configured BeautifulSoupCrawler instance
        """
        return BeautifulSoupCrawler(
            max_requests_per_crawl=self.max_requests_per_crawl,
            max_request_retries=self.max_request_retries,
            request_handler_timeout_secs=30,
            # SCB-specific headers to mimic browser behavior
            headers={
                'User-Agent': 'IRIS-Bot/6.0 (Swedish Data Collector)',
                'Accept': 'text/html,application/json',
                'Accept-Language': 'sv-SE,sv;q=0.9',
            }
        )
    
    def _setup_router(self) -> None:
        """
        Setup SCB request routing.
        
        Configures the router to handle SCB-specific pages and extract
        statistical data using the default handler.
        """
        
        @self.crawler.router.default_handler
        async def handle_scb_page(context: BeautifulSoupCrawlingContext) -> None:
            """
            Handle SCB statistics page.
            
            Args:
                context: Crawlee crawling context with page data
            """
            try:
                logger.info(f"📊 Processing SCB page: {context.request.url}")
                
                # Extract data using our extract_data method
                data = await self.extract_data(context)
                
                # Store extracted data
                await context.push_data(data)
                
                logger.debug(f"✅ Extracted data from {context.request.url}")
                
            except Exception as e:
                logger.error(
                    f"❌ Error processing SCB page {context.request.url}: {e}",
                    exc_info=True
                )
                # Re-raise to trigger retry mechanism
                raise
    
    async def extract_data(
        self,
        context: BeautifulSoupCrawlingContext
    ) -> Dict[str, Any]:
        """
        Extract statistical data from SCB page.
        
        Parses HTML/JSON content from SCB and extracts relevant statistical
        information including population data, economic indicators, etc.
        
        Args:
            context: Crawlee crawling context containing page data
            
        Returns:
            Dictionary with extracted SCB data:
                - källa: Source name ("SCB")
                - url: URL of the page
                - tidsstämpel: Timestamp of extraction (ISO format)
                - titel: Page title if available
                - data: Extracted statistical data
                - status: Extraction status
        
        Raises:
            ValueError: If context is invalid
            Exception: If extraction fails
        
        Example:
            >>> data = await crawler.extract_data(context)
            >>> print(data['källa'])  # "SCB"
            >>> print(data['data']['statistik_typ'])  # e.g., "befolkning"
        """
        if not context:
            raise ValueError("Context cannot be None")
        
        if not context.soup:
            raise ValueError("Context must have soup (parsed HTML)")
        
        soup = context.soup
        url = context.request.url
        
        try:
            # Extract basic information
            title = soup.title.string if soup.title else "Untitled"
            
            # Extract SCB-specific data
            # NOTE: This is a simplified extraction - actual SCB pages
            # have complex structures that need specific parsers
            
            # Look for tables with statistical data
            tables = soup.find_all('table')
            table_data = []
            for table in tables[:5]:  # Limit to first 5 tables
                rows = table.find_all('tr')
                if rows:
                    table_data.append({
                        'rows': len(rows),
                        'first_row': rows[0].get_text(strip=True) if rows else None
                    })
            
            # Look for JSON-LD structured data
            json_ld = soup.find('script', type='application/ld+json')
            structured_data = json_ld.string if json_ld else None
            
            # Build result
            result = {
                "källa": self.source_name,
                "url": url,
                "tidsstämpel": datetime.utcnow().isoformat(),
                "titel": title,
                "data": {
                    "statistik_typ": self._infer_statistics_type(url, title),
                    "antal_tabeller": len(tables),
                    "tabelldata": table_data,
                    "strukturerad_data": structured_data is not None,
                },
                "status": "success"
            }
            
            logger.debug(f"📊 Extracted {len(tables)} tables from SCB page")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Data extraction failed: {e}", exc_info=True)
            
            # Return error data instead of failing completely
            return {
                "källa": self.source_name,
                "url": url,
                "tidsstämpel": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e),
                "data": {}
            }
    
    def _infer_statistics_type(self, url: str, title: str) -> str:
        """
        Infer type of statistics from URL and title.
        
        Args:
            url: Page URL
            title: Page title
            
        Returns:
            Inferred statistics type (e.g., "befolkning", "ekonomi")
        """
        url_lower = url.lower()
        title_lower = title.lower() if title else ""
        
        # Check for common SCB statistics types
        if "befolkning" in url_lower or "befolkning" in title_lower:
            return "befolkning"
        elif "arbetsmarknad" in url_lower or "arbetsmarknad" in title_lower:
            return "arbetsmarknad"
        elif "ekonomi" in url_lower or "ekonomi" in title_lower:
            return "ekonomi"
        elif "utbildning" in url_lower or "utbildning" in title_lower:
            return "utbildning"
        else:
            return "allmän_statistik"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get SCB crawler statistics.
        
        Returns:
            Dictionary with crawler statistics including source info
        """
        stats = super().get_stats()
        stats.update({
            "source_name": self.source_name,
            "base_url": self.base_url,
        })
        return stats
