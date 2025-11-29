"""
Tests for image processing utilities
Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
Phase 1: Backend Unit Tests - Image Processing
"""

import pytest
import io
import base64
from PIL import Image
from utils.image_processing import (
    compress_image,
    image_to_base64,
    get_image_media_type,
    validate_image,
    extract_pdf_text,
    process_upload,
    get_image_dimensions,
    MAX_IMAGE_SIZE,
    MAX_DIMENSION,
)


class TestCompressImage:
    """Tests for compress_image function"""

    def test_small_image_unchanged(self, sample_image_bytes):
        """Small images should not need compression"""
        result = compress_image(sample_image_bytes)
        assert len(result) <= MAX_IMAGE_SIZE
        assert len(result) > 0

    def test_large_image_compressed(self, sample_large_image_bytes):
        """Large images should be compressed under max size"""
        result = compress_image(sample_large_image_bytes)
        assert len(result) <= MAX_IMAGE_SIZE

    def test_rgba_converted_to_rgb(self):
        """RGBA images should be converted to RGB for JPEG compression"""
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        rgba_bytes = buffer.getvalue()
        
        result = compress_image(rgba_bytes)
        assert result is not None
        assert len(result) > 0

    def test_palette_image_converted(self):
        """Palette mode images should be converted"""
        img = Image.new('P', (100, 100))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        palette_bytes = buffer.getvalue()
        
        result = compress_image(palette_bytes)
        assert result is not None

    def test_oversized_dimension_resized(self):
        """Images exceeding max dimension should be resized"""
        img = Image.new('RGB', (5000, 5000), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        large_bytes = buffer.getvalue()
        
        result = compress_image(large_bytes)
        
        # Verify dimensions were reduced
        result_img = Image.open(io.BytesIO(result))
        assert result_img.width <= MAX_DIMENSION
        assert result_img.height <= MAX_DIMENSION


class TestImageToBase64:
    """Tests for image_to_base64 function"""

    def test_valid_image_to_base64(self, sample_image_bytes):
        """Valid image should be converted to base64 string"""
        result = image_to_base64(sample_image_bytes)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_base64_is_valid_and_decodable(self, sample_image_bytes):
        """Base64 output should be decodable"""
        result = image_to_base64(sample_image_bytes)
        decoded = base64.b64decode(result)
        assert len(decoded) > 0
        
        # Should be valid image
        img = Image.open(io.BytesIO(decoded))
        assert img is not None

    def test_large_image_compressed_before_encoding(self, sample_large_image_bytes):
        """Large images should be compressed before base64 encoding"""
        result = image_to_base64(sample_large_image_bytes)
        decoded = base64.b64decode(result)
        assert len(decoded) <= MAX_IMAGE_SIZE


class TestGetImageMediaType:
    """Tests for get_image_media_type function"""

    def test_jpeg_detection(self, sample_image_bytes):
        """JPEG images should be detected correctly"""
        result = get_image_media_type(sample_image_bytes)
        assert result == 'image/jpeg'

    def test_png_detection(self, sample_png_bytes):
        """PNG images should be detected correctly"""
        result = get_image_media_type(sample_png_bytes)
        assert result == 'image/png'

    def test_gif_detection(self):
        """GIF images should be detected correctly"""
        gif_bytes = b'GIF89a' + b'\x00' * 100
        result = get_image_media_type(gif_bytes)
        assert result == 'image/gif'

    def test_webp_detection(self):
        """WebP images should be detected correctly"""
        webp_bytes = b'RIFF' + b'\x00\x00\x00\x00' + b'WEBP' + b'\x00' * 100
        result = get_image_media_type(webp_bytes)
        assert result == 'image/webp'

    def test_unknown_defaults_to_jpeg(self):
        """Unknown formats should default to JPEG"""
        result = get_image_media_type(b'random unknown data here')
        assert result == 'image/jpeg'

    def test_empty_bytes_defaults_to_jpeg(self):
        """Empty bytes should default to JPEG"""
        result = get_image_media_type(b'')
        assert result == 'image/jpeg'


class TestValidateImage:
    """Tests for validate_image function"""

    def test_valid_jpeg_passes(self, sample_image_bytes):
        """Valid JPEG images should pass validation"""
        is_valid, error = validate_image(sample_image_bytes)
        assert is_valid is True
        assert error is None

    def test_valid_png_passes(self, sample_png_bytes):
        """Valid PNG images should pass validation"""
        is_valid, error = validate_image(sample_png_bytes)
        assert is_valid is True
        assert error is None

    def test_invalid_bytes_fails(self):
        """Invalid bytes should fail validation"""
        is_valid, error = validate_image(b'not an image at all')
        assert is_valid is False
        assert error is not None
        assert 'Invalid image' in error

    def test_empty_bytes_fails(self):
        """Empty bytes should fail validation"""
        is_valid, error = validate_image(b'')
        assert is_valid is False
        assert error is not None

    def test_truncated_image_fails(self):
        """Truncated image data should fail"""
        # Only JPEG header without body
        truncated = b'\xff\xd8\xff\xe0'
        is_valid, error = validate_image(truncated)
        assert is_valid is False


class TestExtractPdfText:
    """Tests for extract_pdf_text function"""

    def test_invalid_pdf_returns_error(self):
        """Invalid PDF should return error message"""
        result = extract_pdf_text(b'not a pdf')
        assert 'Error' in result or len(result) == 0

    def test_minimal_pdf_handling(self, sample_pdf_bytes):
        """Should handle minimal PDF bytes without crashing"""
        # This will likely return error, but shouldn't raise exception
        result = extract_pdf_text(sample_pdf_bytes)
        assert isinstance(result, str)


class TestProcessUpload:
    """Tests for process_upload function"""

    def test_process_jpeg_image(self, sample_image_bytes):
        """JPEG processing should return base64 and media type"""
        base64_data, media_type, text = process_upload(
            sample_image_bytes, 'image/jpeg'
        )
        assert base64_data != ""
        assert media_type == 'image/jpeg'
        assert text is None

    def test_process_png_image(self, sample_png_bytes):
        """PNG processing should return base64 and media type"""
        base64_data, media_type, text = process_upload(
            sample_png_bytes, 'image/png'
        )
        assert base64_data != ""
        assert media_type == 'image/png'
        assert text is None

    def test_process_pdf_returns_something(self, sample_pdf_bytes):
        """PDF processing should return either image or text"""
        base64_data, media_type, text = process_upload(
            sample_pdf_bytes, 'application/pdf'
        )
        # Either image conversion or text extraction should work
        assert media_type in ['image/jpeg', 'text/plain']
        if media_type == 'text/plain':
            assert text is not None
        else:
            assert base64_data != ""

    def test_process_pdf_by_magic_bytes(self, sample_pdf_bytes):
        """PDF detection by magic bytes should work"""
        # Even with wrong content type, magic bytes should be detected
        base64_data, media_type, text = process_upload(
            sample_pdf_bytes, 'application/octet-stream'
        )
        # Should detect PDF and process
        assert media_type in ['image/jpeg', 'text/plain']

    def test_invalid_image_raises_valueerror(self):
        """Invalid image bytes should raise ValueError"""
        with pytest.raises(ValueError) as excinfo:
            process_upload(b'invalid image data', 'image/jpeg')
        assert 'Invalid image' in str(excinfo.value)


class TestGetImageDimensions:
    """Tests for get_image_dimensions function"""

    def test_get_correct_dimensions(self, sample_image_bytes):
        """Should return correct image dimensions"""
        width, height = get_image_dimensions(sample_image_bytes)
        assert width == 100
        assert height == 100

    def test_rectangular_dimensions(self):
        """Should return correct dimensions for non-square images"""
        img = Image.new('RGB', (200, 150), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        
        width, height = get_image_dimensions(buffer.getvalue())
        assert width == 200
        assert height == 150

    def test_png_dimensions(self, sample_png_bytes):
        """Should work with PNG images"""
        width, height = get_image_dimensions(sample_png_bytes)
        assert width == 100
        assert height == 100


class TestImageProcessingEdgeCases:
    """Edge case tests for image processing"""

    def test_very_small_image(self):
        """Very small images should be processed"""
        img = Image.new('RGB', (1, 1), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        tiny_bytes = buffer.getvalue()
        
        result = compress_image(tiny_bytes)
        assert len(result) > 0

    def test_single_color_image_compression(self):
        """Single color images should compress well"""
        img = Image.new('RGB', (1000, 1000), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=100)
        mono_bytes = buffer.getvalue()
        
        result = compress_image(mono_bytes)
        assert len(result) <= MAX_IMAGE_SIZE

    def test_grayscale_image(self):
        """Grayscale images should be handled"""
        img = Image.new('L', (100, 100))  # Grayscale mode
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        gray_bytes = buffer.getvalue()
        
        # Should be convertible to base64
        result = image_to_base64(gray_bytes)
        assert isinstance(result, str)
        assert len(result) > 0


