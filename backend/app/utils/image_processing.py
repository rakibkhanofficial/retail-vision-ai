import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple

def validate_image_format(image_data: bytes) -> bool:
    """Validate image format"""
    try:
        Image.open(io.BytesIO(image_data))
        return True
    except Exception:
        return False

def resize_image(image_path: str, max_size: Tuple[int, int] = (1024, 1024)) -> str:
    """Resize image while maintaining aspect ratio"""
    img = Image.open(image_path)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(image_path)
    return image_path

def convert_to_jpg(image_path: str) -> str:
    """Convert image to JPG format"""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
    img.save(jpg_path, 'JPEG', quality=95)
    return jpg_path