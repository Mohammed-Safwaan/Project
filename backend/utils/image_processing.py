"""
Image processing utilities for skin lesion detection
"""

import os
import hashlib
import time
from datetime import datetime
from PIL import Image
import numpy as np
from typing import Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, upload_dir: str = "uploads"):
        """
        Initialize image processor
        
        Args:
            upload_dir (str): Directory to store uploaded images
        """
        self.upload_dir = upload_dir
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
    
    def validate_image(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate uploaded image file
        
        Args:
            file_path (str): Path to image file
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return False, f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (10MB)"
            
            # Check file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.allowed_extensions:
                return False, f"File type {ext} not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            
            # Try to open and validate image
            with Image.open(file_path) as img:
                # Check image mode
                if img.mode not in ['RGB', 'RGBA', 'L']:
                    return False, f"Unsupported image mode: {img.mode}"
                
                # Check minimum dimensions
                if img.size[0] < 50 or img.size[1] < 50:
                    return False, "Image dimensions too small (minimum 50x50 pixels)"
                
                # Check maximum dimensions
                if img.size[0] > 4000 or img.size[1] > 4000:
                    return False, "Image dimensions too large (maximum 4000x4000 pixels)"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """
        Generate secure filename with timestamp and hash
        
        Args:
            original_filename (str): Original filename
            
        Returns:
            str: Secure filename
        """
        # Get file extension
        _, ext = os.path.splitext(original_filename.lower())
        
        # Generate hash from original filename and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{original_filename}_{timestamp}_{time.time()}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        # Create secure filename
        secure_filename = f"skin_{timestamp}_{file_hash}{ext}"
        
        return secure_filename
    
    def save_uploaded_image(self, file_data: bytes, filename: str) -> Dict:
        """
        Save uploaded image to disk
        
        Args:
            file_data (bytes): Image file data
            filename (str): Original filename
            
        Returns:
            Dict: Image information including path, size, etc.
        """
        try:
            # Generate secure filename
            secure_filename = self.generate_secure_filename(filename)
            file_path = os.path.join(self.upload_dir, secure_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Validate the saved image
            is_valid, error_message = self.validate_image(file_path)
            if not is_valid:
                # Clean up invalid file
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise ValueError(error_message)
            
            # Get image information
            with Image.open(file_path) as img:
                image_info = {
                    'filename': secure_filename,
                    'original_filename': filename,
                    'path': file_path,
                    'size': {
                        'width': img.size[0],
                        'height': img.size[1],
                        'mode': img.mode
                    },
                    'file_size_bytes': os.path.getsize(file_path),
                    'created_at': datetime.now().isoformat()
                }
            
            logger.info(f"Image saved successfully: {secure_filename}")
            return image_info
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise
    
    def preprocess_for_display(self, image_path: str, max_size: Tuple[int, int] = (800, 600)) -> str:
        """
        Create a web-optimized version of the image for display
        
        Args:
            image_path (str): Path to original image
            max_size (Tuple[int, int]): Maximum dimensions for display
            
        Returns:
            str: Path to optimized image
        """
        try:
            # Generate display version filename
            base_name, ext = os.path.splitext(image_path)
            display_path = f"{base_name}_display{ext}"
            
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate new size maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(display_path, 'JPEG', quality=85, optimize=True)
            
            logger.info(f"Display version created: {display_path}")
            return display_path
            
        except Exception as e:
            logger.error(f"Error creating display version: {str(e)}")
            return image_path  # Return original if optimization fails
    
    def get_image_info(self, image_path: str) -> Dict:
        """
        Get detailed information about an image
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            Dict: Detailed image information
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            with Image.open(image_path) as img:
                # Get basic info
                info = {
                    'filename': os.path.basename(image_path),
                    'path': image_path,
                    'size': {
                        'width': img.size[0],
                        'height': img.size[1],
                        'mode': img.mode
                    },
                    'file_size_bytes': os.path.getsize(image_path),
                    'format': img.format,
                }
                
                # Add EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    info['exif'] = exif
                
                # Calculate aspect ratio
                aspect_ratio = img.size[0] / img.size[1]
                info['aspect_ratio'] = round(aspect_ratio, 2)
                
                # Add creation time from file system
                stat = os.stat(image_path)
                info['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                info['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            raise
    
    def cleanup_old_images(self, days_old: int = 7) -> int:
        """
        Clean up old uploaded images
        
        Args:
            days_old (int): Remove images older than this many days
            
        Returns:
            int: Number of images deleted
        """
        try:
            deleted_count = 0
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"Deleted old image: {filename}")
                        except Exception as e:
                            logger.warning(f"Could not delete {filename}: {str(e)}")
            
            logger.info(f"Cleaned up {deleted_count} old images")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old images: {str(e)}")
            raise
    
    def delete_image(self, image_path: str) -> bool:
        """
        Delete specific image file
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                
                # Also try to remove display version
                base_name, ext = os.path.splitext(image_path)
                display_path = f"{base_name}_display{ext}"
                if os.path.exists(display_path):
                    os.remove(display_path)
                
                logger.info(f"Image deleted: {image_path}")
                return True
            else:
                logger.warning(f"Image not found for deletion: {image_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            return False

# Utility function for easy access
def get_image_processor(upload_dir: str = None) -> ImageProcessor:
    """Get image processor instance"""
    if upload_dir is None:
        # Default to backend uploads directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(backend_dir, 'uploads')
    
    return ImageProcessor(upload_dir)