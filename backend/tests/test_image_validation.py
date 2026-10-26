import io
import pytest
from PIL import Image
from app.core.security import validate_image_file, load_and_preprocess_image

def test_empty_file_rejected():
    valid, msg, mime = validate_image_file(b"")
    assert not valid
    assert "empty" in msg.lower()

def test_oversized_file_rejected():
    large_bytes = b"0" * (11 * 1024 * 1024)
    valid, msg, mime = validate_image_file(large_bytes, max_bytes=10 * 1024 * 1024)
    assert not valid
    assert "exceeds" in msg.lower()

def test_invalid_magic_bytes_rejected():
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
    valid, msg, mime = validate_image_file(fake_exe)
    assert not valid
    assert "unsupported" in msg.lower()

def test_valid_jpeg_accepted():
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    jpeg_bytes = buf.getvalue()
    
    valid, msg, mime = validate_image_file(jpeg_bytes)
    assert valid
    assert mime == "image/jpeg"

    arr, dims = load_and_preprocess_image(jpeg_bytes)
    assert arr.shape == (100, 100, 3)
    assert dims == (100, 100)

def test_valid_png_accepted():
    img = Image.new("RGBA", (80, 80), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    
    valid, msg, mime = validate_image_file(png_bytes)
    assert valid
    assert mime == "image/png"

    arr, dims = load_and_preprocess_image(png_bytes)
    assert arr.shape == (80, 80, 3)  # Converted to RGB
