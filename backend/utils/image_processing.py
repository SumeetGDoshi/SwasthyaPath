"""
Image processing utilities for medical report uploads
"""

import base64
import io
from typing import Tuple, Optional
from PIL import Image
import PyPDF2


# Maximum image size for Claude API (in bytes) - 20MB limit, we use 4MB for safety
MAX_IMAGE_SIZE = 4 * 1024 * 1024  # 4MB
MAX_DIMENSION = 2048  # Max width/height


def compress_image(image_bytes: bytes, max_size: int = MAX_IMAGE_SIZE) -> bytes:
    """
    Compress image if it exceeds the maximum size
    """
    if len(image_bytes) <= max_size:
        return image_bytes
    
    # Open image
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if necessary (for JPEG compression)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if too large
    if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
    
    # Compress with decreasing quality until under max size
    quality = 85
    while quality > 20:
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        compressed = buffer.getvalue()
        
        if len(compressed) <= max_size:
            return compressed
        
        quality -= 10
    
    # Return whatever we got at minimum quality
    return compressed


def image_to_base64(image_bytes: bytes) -> str:
    """
    Convert image bytes to base64 string
    """
    # Compress if needed
    compressed = compress_image(image_bytes)
    return base64.b64encode(compressed).decode('utf-8')


def get_image_media_type(image_bytes: bytes) -> str:
    """
    Detect image media type from bytes
    """
    # Check magic bytes
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'image/png'
    elif image_bytes[:2] == b'\xff\xd8':
        return 'image/jpeg'
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return 'image/gif'
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return 'image/webp'
    else:
        # Default to JPEG
        return 'image/jpeg'


def validate_image(image_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validate that the bytes represent a valid image
    Returns (is_valid, error_message)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # Verify it's a valid image
        
        # Check file size
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            return False, "Image size exceeds 10MB limit"
        
        return True, None
    except Exception as e:
        return False, f"Invalid image: {str(e)}"


def extract_pdf_first_page(pdf_bytes: bytes) -> Optional[bytes]:
    """
    Extract the first page of a PDF as an image
    Note: Requires poppler for pdf2image, fallback to text extraction
    """
    try:
        # Try using pdf2image if poppler is available
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
        if images:
            buffer = io.BytesIO()
            images[0].save(buffer, format='JPEG', quality=85)
            return buffer.getvalue()
    except ImportError:
        pass
    except Exception:
        pass
    
    return None


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF as fallback
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages[:5]:  # First 5 pages max
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def process_upload(file_bytes: bytes, content_type: str) -> Tuple[str, str, Optional[str]]:
    """
    Process an uploaded file and return (base64_data, media_type, extracted_text)
    
    For images: returns base64 and media type
    For PDFs: attempts image conversion, falls back to text extraction
    """
    if content_type == 'application/pdf' or file_bytes[:4] == b'%PDF':
        # Try to convert PDF to image
        image_bytes = extract_pdf_first_page(file_bytes)
        if image_bytes:
            base64_data = image_to_base64(image_bytes)
            return base64_data, 'image/jpeg', None
        else:
            # Fallback to text extraction
            text = extract_pdf_text(file_bytes)
            return "", "text/plain", text
    else:
        # Process as image
        is_valid, error = validate_image(file_bytes)
        if not is_valid:
            raise ValueError(error)
        
        base64_data = image_to_base64(file_bytes)
        media_type = get_image_media_type(file_bytes)
        return base64_data, media_type, None


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Get image width and height
    """
    img = Image.open(io.BytesIO(image_bytes))
    return img.size


