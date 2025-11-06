"""
Crawlee-based web crawlers for IRIS data collection.

This module provides robust web scraping capabilities for Swedish data sources
using the Crawlee framework. Includes automatic retries, session management,
and anti-blocking features.
"""

from .base import BaseSwedishCrawler
from .scb_crawler import SCBCrawler

__all__ = [
    'BaseSwedishCrawler',
    'SCBCrawler',
]

__version__ = '1.0.0'
