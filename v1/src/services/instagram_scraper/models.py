"""
IRIS v6.0 - Instagram Scraper Models
Pydantic models for Instagram data structures
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Instagram content types."""
    IMAGE = "Image"
    VIDEO = "Video"
    CAROUSEL = "Carousel"
    REEL = "Reel"


class InstagramProfile(BaseModel):
    """Instagram profile model."""
    username: str = Field(..., description="Instagram username")
    full_name: Optional[str] = Field(None, description="Full display name")
    biography: Optional[str] = Field(None, description="Profile bio")
    followers: int = Field(0, description="Follower count")
    following: int = Field(0, description="Following count")
    posts_count: int = Field(0, description="Total posts")
    profile_pic_url: Optional[str] = Field(None, description="Profile picture URL")
    is_verified: bool = Field(False, description="Verified account")
    is_private: bool = Field(False, description="Private account")
    external_url: Optional[str] = Field(None, description="Bio URL")
    user_id: Optional[str] = Field(None, description="Instagram user ID")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "username": "natgeo",
                "full_name": "National Geographic",
                "biography": "Experience the world through the eyes of National Geographic",
                "followers": 280000000,
                "following": 200,
                "posts_count": 25000,
                "is_verified": True,
                "is_private": False
            }
        }


class InstagramLocation(BaseModel):
    """Instagram location/place model."""
    id: Optional[str] = Field(None, description="Location ID")
    name: Optional[str] = Field(None, description="Location name")
    slug: Optional[str] = Field(None, description="Location slug")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")


class InstagramPost(BaseModel):
    """Instagram post model with complete metadata."""
    url: str = Field(..., description="Post URL")
    shortcode: str = Field(..., description="Instagram shortcode")
    type: ContentType = Field(..., description="Content type")
    caption: Optional[str] = Field(None, description="Post caption")
    hashtags: List[str] = Field(default_factory=list, description="Extracted hashtags")
    mentions: List[str] = Field(default_factory=list, description="Mentioned usernames")
    likes_count: int = Field(0, description="Number of likes")
    comments_count: int = Field(0, description="Number of comments")
    timestamp: Optional[datetime] = Field(None, description="Post creation time")
    
    # Media URLs
    display_url: Optional[str] = Field(None, description="Main image URL")
    images: List[str] = Field(default_factory=list, description="Additional carousel images")
    video_url: Optional[str] = Field(None, description="Video URL if applicable")
    thumbnail_url: Optional[str] = Field(None, description="Video thumbnail URL")
    
    # Dimensions
    dimensions_height: Optional[int] = Field(None, description="Image height")
    dimensions_width: Optional[int] = Field(None, description="Image width")
    
    # Owner info
    owner_username: str = Field(..., description="Post owner username")
    owner_full_name: Optional[str] = Field(None, description="Post owner full name")
    owner_id: Optional[str] = Field(None, description="Post owner user ID")
    owner_profile_pic: Optional[str] = Field(None, description="Owner profile pic URL")
    
    # Additional metadata
    location: Optional[InstagramLocation] = Field(None, description="Post location")
    is_sponsored: bool = Field(False, description="Sponsored post")
    is_video: bool = Field(False, description="Is video content")
    video_view_count: Optional[int] = Field(None, description="Video views")
    alt_text: Optional[str] = Field(None, description="Image alt text")
    
    # Local storage paths (populated after download)
    local_image_paths: List[str] = Field(default_factory=list, description="Downloaded image paths")
    metadata_json_path: Optional[str] = Field(None, description="Metadata JSON path")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "url": "https://www.instagram.com/p/ABC123/",
                "shortcode": "ABC123",
                "type": "Image",
                "caption": "Beautiful sunset 🌅 #nature #sunset",
                "hashtags": ["nature", "sunset"],
                "mentions": [],
                "likes_count": 5000,
                "comments_count": 250,
                "owner_username": "photographer",
                "is_sponsored": False
            }
        }


class InstagramComment(BaseModel):
    """Instagram comment model."""
    comment_id: str = Field(..., description="Comment ID")
    text: str = Field(..., description="Comment text")
    owner_username: str = Field(..., description="Comment author username")
    owner_id: Optional[str] = Field(None, description="Comment author user ID")
    timestamp: Optional[datetime] = Field(None, description="Comment creation time")
    likes_count: int = Field(0, description="Comment likes")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "comment_id": "123456789",
                "text": "Amazing photo!",
                "owner_username": "user123",
                "likes_count": 10
            }
        }


class InstagramHashtag(BaseModel):
    """Instagram hashtag model."""
    name: str = Field(..., description="Hashtag name (without #)")
    posts_count: int = Field(0, description="Total posts with hashtag")
    profile_pic_url: Optional[str] = Field(None, description="Hashtag profile picture")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "name": "nature",
                "posts_count": 500000000
            }
        }


class ScrapeRequest(BaseModel):
    """Request model for scraping operations."""
    target: str = Field(..., description="Username, URL, or hashtag to scrape")
    scrape_type: str = Field("profile", description="Type: profile, post, hashtag, location")
    max_posts: int = Field(50, ge=1, le=500, description="Maximum posts to scrape")
    download_images: bool = Field(True, description="Download images")
    download_videos: bool = Field(False, description="Download videos")
    include_comments: bool = Field(False, description="Scrape comments")
    max_comments_per_post: int = Field(50, ge=0, le=1000, description="Max comments")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "target": "natgeo",
                "scrape_type": "profile",
                "max_posts": 20,
                "download_images": True
            }
        }


class ScrapeResult(BaseModel):
    """Result model for scraping operations."""
    success: bool = Field(..., description="Operation success")
    target: str = Field(..., description="Scraped target")
    scrape_type: str = Field(..., description="Scrape type")
    posts_scraped: int = Field(0, description="Number of posts scraped")
    images_downloaded: int = Field(0, description="Number of images downloaded")
    videos_downloaded: int = Field(0, description="Number of videos downloaded")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    duration_seconds: float = Field(0.0, description="Operation duration")
    storage_path: Optional[str] = Field(None, description="Local storage path")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "target": "natgeo",
                "scrape_type": "profile",
                "posts_scraped": 20,
                "images_downloaded": 20,
                "duration_seconds": 45.2,
                "storage_path": "data/instagram/natgeo"
            }
        }


class DownloadProgress(BaseModel):
    """Progress model for download operations."""
    total_items: int = Field(0, description="Total items to download")
    completed_items: int = Field(0, description="Completed items")
    failed_items: int = Field(0, description="Failed items")
    progress_percentage: float = Field(0.0, description="Progress percentage")
    current_file: Optional[str] = Field(None, description="Currently downloading file")
    estimated_time_remaining: Optional[float] = Field(None, description="ETA in seconds")
    
    @property
    def is_complete(self) -> bool:
        """Check if download is complete."""
        return self.completed_items + self.failed_items >= self.total_items
