"""
Shared pytest fixtures for Tag Writer tests.
"""

import sys
import os

# Ensure src/ is on the path so tag_writer package can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest


@pytest.fixture
def sample_jpeg(tmp_path):
    """Create a minimal test JPEG image in a temp directory."""
    from PIL import Image
    img = Image.new('RGB', (100, 80), color=(200, 100, 50))
    path = tmp_path / "test_image.jpg"
    img.save(str(path), format='JPEG')
    return str(path)


@pytest.fixture
def sample_png(tmp_path):
    """Create a minimal test PNG image in a temp directory."""
    from PIL import Image
    img = Image.new('RGB', (60, 40), color=(50, 150, 200))
    path = tmp_path / "test_image.png"
    img.save(str(path), format='PNG')
    return str(path)


@pytest.fixture
def image_directory(tmp_path):
    """Create a temp directory with a mix of image and non-image files."""
    from PIL import Image
    entries = [
        ("photo_a.jpg", "JPEG"),
        ("photo_b.jpeg", "JPEG"),
        ("photo_c.png", "PNG"),
        ("photo_d.tif", "TIFF"),
        ("document.txt", None),
        ("notes.pdf", None),
    ]
    for name, fmt in entries:
        path = tmp_path / name
        if fmt:
            img = Image.new('RGB', (10, 10), color=(0, 0, 0))
            img.save(str(path), format=fmt)
        else:
            path.write_text("placeholder")
    return str(tmp_path)


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    """
    Redirect Config's file path to tmp_path so tests don't touch
    the real ~/.tag_writer_config.json.
    """
    monkeypatch.setattr("os.path.expanduser", lambda _: str(tmp_path))
    return tmp_path


@pytest.fixture
def fresh_config(config_dir):
    """A fresh Config instance backed by a temp directory."""
    from tag_writer.config import Config
    return Config()
