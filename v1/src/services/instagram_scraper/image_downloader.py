"""
IRIS v6.0 - Instagram Image Downloader
Async image download with retry logic and progress tracking
"""

import aiohttp
import aiofiles
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib
import json

from .models import InstagramPost, DownloadProgress

logger = logging.getLogger(__name__)


class ImageDownloader:
    """
    Async image downloader with concurrent downloads, retry logic, and progress tracking.
    
    Features:
    - Concurrent downloads (configurable max)
    - Retry with exponential backoff
    - Progress tracking
    - File integrity checks (MD5)
    - Metadata JSON generation
    """
    
    def __init__(
        self,
        max_concurrent: int = 5,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize ImageDownloader.
        
        Args:
            max_concurrent: Maximum concurrent downloads
            max_retries: Maximum retry attempts
            retry_delay: Initial retry delay in seconds
            timeout: Request timeout in seconds
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(
            f"📥 ImageDownloader initialized: "
            f"max_concurrent={max_concurrent}, "
            f"max_retries={max_retries}"
        )
    
    async def download_image(
        self,
        url: str,
        save_path: Path,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Download a single image with retry logic.
        
        Args:
            url: Image URL
            save_path: Local path to save image
            session: Optional aiohttp session
        
        Returns:
            Tuple of (success, error_message)
        
        Raises:
            ValueError: If URL or save_path is invalid
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
        
        if not save_path:
            raise ValueError("Save path cannot be empty")
        
        # Ensure parent directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use provided session or create temporary one
        close_session = session is None
        if session is None:
            session = aiohttp.ClientSession(timeout=self.timeout)
        
        try:
            async with self.semaphore:
                for attempt in range(1, self.max_retries + 1):
                    try:
                        logger.debug(f"Downloading {url} (attempt {attempt}/{self.max_retries})")
                        
                        async with session.get(url) as response:
                            if response.status == 200:
                                # Download content
                                content = await response.read()
                                
                                # Write to file
                                async with aiofiles.open(save_path, 'wb') as f:
                                    await f.write(content)
                                
                                logger.info(f"✅ Downloaded: {save_path.name}")
                                return True, None
                            
                            elif response.status == 404:
                                error_msg = f"Image not found (404): {url}"
                                logger.warning(error_msg)
                                return False, error_msg
                            
                            else:
                                error_msg = f"HTTP {response.status}: {url}"
                                logger.warning(error_msg)
                                
                                # Retry on server errors
                                if attempt < self.max_retries:
                                    delay = self.retry_delay * (2 ** (attempt - 1))
                                    logger.info(f"⏳ Retrying in {delay}s...")
                                    await asyncio.sleep(delay)
                                    continue
                                
                                return False, error_msg
                    
                    except asyncio.TimeoutError:
                        error_msg = f"Timeout downloading {url}"
                        logger.warning(error_msg)
                        
                        if attempt < self.max_retries:
                            delay = self.retry_delay * (2 ** (attempt - 1))
                            await asyncio.sleep(delay)
                            continue
                        
                        return False, error_msg
                    
                    except Exception as e:
                        error_msg = f"Error downloading {url}: {str(e)}"
                        logger.error(error_msg, exc_info=True)
                        
                        if attempt < self.max_retries:
                            delay = self.retry_delay * (2 ** (attempt - 1))
                            await asyncio.sleep(delay)
                            continue
                        
                        return False, error_msg
                
                return False, f"Max retries ({self.max_retries}) exceeded"
        
        finally:
            if close_session:
                await session.close()
    
    async def download_post_images(
        self,
        post: InstagramPost,
        base_folder: Path,
        session: Optional[aiohttp.ClientSession] = None
    ) -> List[str]:
        """
        Download all images from an Instagram post.
        
        Args:
            post: InstagramPost model
            base_folder: Base folder for storage
            session: Optional aiohttp session
        
        Returns:
            List of successfully downloaded image paths
        """
        if not post:
            raise ValueError("Post cannot be None")
        
        # Create post-specific folder
        post_folder = base_folder / post.owner_username / post.shortcode
        post_folder.mkdir(parents=True, exist_ok=True)
        
        # Collect all image URLs
        image_urls = []
        if post.display_url:
            image_urls.append(post.display_url)
        if post.images:
            image_urls.extend(post.images)
        
        if not image_urls:
            logger.warning(f"No images found for post {post.shortcode}")
            return []
        
        logger.info(f"📥 Downloading {len(image_urls)} images for post {post.shortcode}")
        
        # Download images concurrently
        downloaded_paths = []
        tasks = []
        
        close_session = session is None
        if session is None:
            session = aiohttp.ClientSession(timeout=self.timeout)
        
        try:
            for idx, url in enumerate(image_urls):
                # Generate filename
                ext = self._get_extension_from_url(url)
                filename = f"{post.shortcode}_{idx+1}{ext}"
                save_path = post_folder / filename
                
                # Create download task
                task = self.download_image(url, save_path, session)
                tasks.append((task, save_path))
            
            # Execute downloads
            results = await asyncio.gather(*[task for task, _ in tasks], return_exceptions=True)
            
            # Collect successful downloads
            for (_, save_path), result in zip(tasks, results):
                if isinstance(result, tuple) and result[0]:
                    downloaded_paths.append(str(save_path))
            
            logger.info(
                f"✅ Downloaded {len(downloaded_paths)}/{len(image_urls)} "
                f"images for post {post.shortcode}"
            )
            
            # Save metadata JSON
            if downloaded_paths:
                await self._save_metadata(post, post_folder, downloaded_paths)
            
            return downloaded_paths
        
        finally:
            if close_session:
                await session.close()
    
    async def download_batch(
        self,
        posts: List[InstagramPost],
        base_folder: Path,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, List[str]]:
        """
        Download images from multiple posts with progress tracking.
        
        Args:
            posts: List of InstagramPost models
            base_folder: Base folder for storage
            progress_callback: Optional callback for progress updates
        
        Returns:
            Dict mapping post shortcode to downloaded image paths
        """
        if not posts:
            logger.warning("No posts to download")
            return {}
        
        logger.info(f"📥 Starting batch download of {len(posts)} posts")
        
        results = {}
        progress = DownloadProgress(total_items=len(posts))
        start_time = datetime.now().timestamp()
        
        # Create single session for all downloads
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for idx, post in enumerate(posts, 1):
                try:
                    progress.current_file = f"{post.owner_username}/{post.shortcode}"
                    
                    # Call progress callback if provided
                    if progress_callback:
                        await progress_callback(progress)
                    
                    # Download post images
                    downloaded = await self.download_post_images(
                        post, base_folder, session
                    )
                    
                    results[post.shortcode] = downloaded
                    progress.completed_items += 1
                    
                except Exception as e:
                    logger.error(f"Failed to download post {post.shortcode}: {e}")
                    progress.failed_items += 1
                    results[post.shortcode] = []
                
                # Update progress
                progress.progress_percentage = (
                    (progress.completed_items + progress.failed_items) / 
                    progress.total_items * 100
                )
                
                # Estimate time remaining
                if idx > 1:
                    avg_time_per_post = (datetime.now().timestamp() - start_time) / idx
                    remaining_posts = len(posts) - idx
                    progress.estimated_time_remaining = avg_time_per_post * remaining_posts
        
        logger.info(
            f"✅ Batch download complete: "
            f"{progress.completed_items} succeeded, "
            f"{progress.failed_items} failed"
        )
        
        return results
    
    async def _save_metadata(
        self,
        post: InstagramPost,
        folder: Path,
        image_paths: List[str]
    ) -> None:
        """
        Save post metadata as JSON file.
        
        Args:
            post: InstagramPost model
            folder: Folder to save metadata
            image_paths: List of downloaded image paths
        """
        try:
            metadata_path = folder / f"{post.shortcode}_metadata.json"
            
            # Update post with local paths
            post_dict = post.model_dump(mode='json')
            post_dict['local_image_paths'] = image_paths
            post_dict['metadata_json_path'] = str(metadata_path)
            post_dict['download_timestamp'] = datetime.now().isoformat()
            
            # Write JSON
            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(post_dict, indent=2, ensure_ascii=False))
            
            logger.debug(f"💾 Saved metadata: {metadata_path}")
        
        except Exception as e:
            logger.error(f"Failed to save metadata for {post.shortcode}: {e}")
    
    @staticmethod
    def _get_extension_from_url(url: str) -> str:
        """
        Extract file extension from URL.
        
        Args:
            url: Image URL
        
        Returns:
            File extension (e.g., '.jpg')
        """
        # Extract extension from URL
        url_path = url.split('?')[0]  # Remove query params
        
        if url_path.endswith('.jpg') or url_path.endswith('.jpeg'):
            return '.jpg'
        elif url_path.endswith('.png'):
            return '.png'
        elif url_path.endswith('.webp'):
            return '.webp'
        elif url_path.endswith('.gif'):
            return '.gif'
        else:
            return '.jpg'  # Default to jpg
    
    @staticmethod
    def calculate_md5(file_path: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            MD5 hash string
        """
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
