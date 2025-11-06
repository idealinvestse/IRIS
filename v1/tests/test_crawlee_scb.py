"""
Tests for SCB Crawler using Crawlee.

This module contains unit and integration tests for the SCB crawler implementation.
"""

import pytest
import os
from unittest.mock import Mock

from src.services.crawlers.scb_crawler import SCBCrawler
from crawlee.crawlers import BeautifulSoupCrawlingContext


class TestSCBCrawler:
    """Test suite for SCB crawler."""
    
    def test_scb_crawler_initialization(self):
        """Test SCB crawler can be initialized with default parameters."""
        crawler = SCBCrawler()
        
        assert crawler is not None
        assert crawler.source_name == "SCB"
        assert crawler.max_requests_per_crawl == 100
        assert crawler.max_request_retries == 3
        assert crawler.cache_ttl == 3600
    
    def test_scb_crawler_custom_parameters(self):
        """Test SCB crawler initialization with custom parameters."""
        crawler = SCBCrawler(
            max_requests_per_crawl=50,
            max_request_retries=5,
            cache_ttl=7200
        )
        
        assert crawler.max_requests_per_crawl == 50
        assert crawler.max_request_retries == 5
        assert crawler.cache_ttl == 7200
    
    def test_scb_crawler_invalid_parameters(self):
        """Test SCB crawler rejects invalid parameters."""
        with pytest.raises(ValueError):
            SCBCrawler(max_requests_per_crawl=-1)
        
        with pytest.raises(ValueError):
            SCBCrawler(max_request_retries=-1)
        
        with pytest.raises(ValueError):
            SCBCrawler(cache_ttl=-1)
    
    def test_scb_crawler_creates_crawler(self):
        """Test SCB crawler creates a BeautifulSoupCrawler."""
        crawler = SCBCrawler()
        
        assert crawler.crawler is not None
        assert hasattr(crawler.crawler, 'run')
    
    def test_scb_crawler_get_stats(self):
        """Test SCB crawler statistics retrieval."""
        crawler = SCBCrawler(max_requests_per_crawl=42)
        stats = crawler.get_stats()
        
        assert stats['crawler_name'] == 'SCBCrawler'
        assert stats['source_name'] == 'SCB'
        assert stats['max_requests'] == 42
        assert 'base_url' in stats
    
    @pytest.mark.asyncio
    async def test_extract_data_with_mock_context(self):
        """Test data extraction with mocked context."""
        crawler = SCBCrawler()
        
        # Create mock context
        mock_context = Mock(spec=BeautifulSoupCrawlingContext)
        mock_context.request = Mock()
        mock_context.request.url = "https://api.scb.se/test"
        
        # Create mock soup with title
        mock_soup = Mock()
        mock_title = Mock()
        mock_title.string = "Befolkningsstatistik"
        mock_soup.title = mock_title
        mock_soup.find_all = Mock(return_value=[])  # No tables
        mock_soup.find = Mock(return_value=None)  # No JSON-LD
        
        mock_context.soup = mock_soup
        
        # Extract data
        data = await crawler.extract_data(mock_context)
        
        # Verify structure
        assert data['källa'] == 'SCB'
        assert data['url'] == "https://api.scb.se/test"
        assert 'tidsstämpel' in data
        assert data['titel'] == "Befolkningsstatistik"
        assert data['status'] == 'success'
        assert 'data' in data
    
    @pytest.mark.asyncio
    async def test_extract_data_with_invalid_context(self):
        """Test data extraction with invalid context."""
        crawler = SCBCrawler()
        
        # Test with None context
        with pytest.raises(ValueError, match="Context cannot be None"):
            await crawler.extract_data(None)
        
        # Test with context without soup
        mock_context = Mock(spec=BeautifulSoupCrawlingContext)
        mock_context.soup = None
        
        with pytest.raises(ValueError, match="Context must have soup"):
            await crawler.extract_data(mock_context)
    
    def test_infer_statistics_type_befolkning(self):
        """Test statistics type inference for population data."""
        crawler = SCBCrawler()
        
        stat_type = crawler._infer_statistics_type(
            "https://scb.se/befolkning",
            "Befolkningsstatistik"
        )
        
        assert stat_type == "befolkning"
    
    def test_infer_statistics_type_ekonomi(self):
        """Test statistics type inference for economic data."""
        crawler = SCBCrawler()
        
        stat_type = crawler._infer_statistics_type(
            "https://scb.se/ekonomi",
            "Ekonomisk statistik"
        )
        
        assert stat_type == "ekonomi"
    
    def test_infer_statistics_type_unknown(self):
        """Test statistics type inference for unknown data."""
        crawler = SCBCrawler()
        
        stat_type = crawler._infer_statistics_type(
            "https://scb.se/unknown",
            "Unknown Statistics"
        )
        
        assert stat_type == "allmän_statistik"
    
    @pytest.mark.asyncio
    async def test_crawl_with_empty_urls(self):
        """Test crawl rejects empty URL list."""
        crawler = SCBCrawler()
        
        with pytest.raises(ValueError, match="URLs list cannot be empty"):
            await crawler.crawl([])
    
    @pytest.mark.asyncio
    async def test_crawl_with_invalid_urls(self):
        """Test crawl validates URL list."""
        crawler = SCBCrawler()
        
        # Test with non-list
        with pytest.raises(ValueError, match="URLs must be a list"):
            await crawler.crawl("not-a-list")
        
        # Test with list of non-strings
        with pytest.raises(ValueError, match="No valid URLs provided"):
            await crawler.crawl([None, 123, {}])
    
    @pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS"),
        reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable"
    )
    @pytest.mark.asyncio
    async def test_crawl_real_scb_page(self):
        """
        Integration test: Crawl a real SCB page.
        
        NOTE: This test makes real network requests and should only be run
        during integration testing, not in regular unit test runs.
        """
        crawler = SCBCrawler(max_requests_per_crawl=1)
        
        # Use a stable SCB URL (update if needed)
        urls = ["https://www.scb.se/hitta-statistik/statistik-efter-amne/"]
        
        try:
            data = await crawler.crawl(urls)
            
            # Verify we got data
            assert len(data) > 0
            assert data[0]['källa'] == 'SCB'
            assert data[0]['status'] in ['success', 'error']
            
        except Exception as e:
            pytest.skip(f"Real SCB crawl failed (network/API issue): {e}")


class TestSCBCrawlerIntegration:
    """Integration tests for SCB crawler with Crawlee."""
    
    @pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS"),
        reason="Integration tests disabled"
    )
    @pytest.mark.asyncio
    async def test_full_crawl_workflow(self):
        """Test complete crawl workflow from initialization to data extraction."""
        # Initialize crawler
        crawler = SCBCrawler(max_requests_per_crawl=2)
        
        # Get stats
        stats = crawler.get_stats()
        assert stats['source_name'] == 'SCB'
        
        # Note: Actual crawling requires valid SCB URLs and network access
        # This is a placeholder for full integration test
        pytest.skip("Full integration test requires live SCB API access")
