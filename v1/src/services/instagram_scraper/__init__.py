"""
IRIS v6.0 - Instagram Scraper Module
"""

from .scraper import InstagramScraper, InstagramScraperException, PrivateProfileException
from .image_downloader import ImageDownloader
from .models import (
    InstagramPost,
    InstagramProfile,
    InstagramHashtag,
    InstagramComment,
    InstagramLocation,
    ContentType,
    ScrapeRequest,
    ScrapeResult,
    DownloadProgress
)

__all__ = [
    'InstagramScraper',
    'InstagramScraperException',
    'PrivateProfileException',
    'ImageDownloader',
    'InstagramPost',
    'InstagramProfile',
    'InstagramHashtag',
    'InstagramComment',
    'InstagramLocation',
    'ContentType',
    'ScrapeRequest',
    'ScrapeResult',
    'DownloadProgress'
]

__version__ = '1.0.0'
