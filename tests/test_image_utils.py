"""
Tests for tag_writer.image_utils — PIL-based operations.
pil_to_pixmap is Qt-dependent and not tested here.
"""

import pytest

# image_utils imports PyQt6 at module level; skip entire file if unavailable
image_utils = pytest.importorskip(
    "tag_writer.image_utils",
    reason="tag_writer.image_utils unavailable (Qt or Pillow missing)",
)

from tag_writer.image_utils import create_thumbnail, adjust_zoom

try:
    from PIL import Image as _PIL_Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

pytestmark = pytest.mark.skipif(not PIL_AVAILABLE, reason="Pillow not installed")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rgb_image():
    from PIL import Image
    return Image.new("RGB", (400, 300), color=(100, 150, 200))


@pytest.fixture
def small_image():
    from PIL import Image
    return Image.new("RGB", (50, 30), color=(255, 0, 0))


# ---------------------------------------------------------------------------
# create_thumbnail
# ---------------------------------------------------------------------------

class TestCreateThumbnail:
    def test_returns_pil_image(self, rgb_image):
        thumb = create_thumbnail(rgb_image, (100, 100))
        assert thumb is not None

    def test_respects_max_width(self, rgb_image):
        thumb = create_thumbnail(rgb_image, (100, 100))
        assert thumb.width <= 100

    def test_respects_max_height(self, rgb_image):
        thumb = create_thumbnail(rgb_image, (100, 100))
        assert thumb.height <= 100

    def test_preserves_aspect_ratio(self, rgb_image):
        # 400x300 is 4:3; thumbnailing to 200x200 must keep ~4:3
        thumb = create_thumbnail(rgb_image, (200, 200))
        ratio_orig = 400 / 300
        ratio_thumb = thumb.width / thumb.height
        assert abs(ratio_orig - ratio_thumb) < 0.1

    def test_none_input_returns_none(self):
        assert create_thumbnail(None, (100, 100)) is None

    def test_small_image_not_enlarged(self, small_image):
        # 50x30 → thumbnailing to 200x200 must not make it bigger
        thumb = create_thumbnail(small_image, (200, 200))
        assert thumb.width <= 50
        assert thumb.height <= 30

    def test_large_max_size_accepted(self, rgb_image):
        thumb = create_thumbnail(rgb_image, (4000, 4000))
        assert thumb is not None


# ---------------------------------------------------------------------------
# adjust_zoom
# ---------------------------------------------------------------------------

class TestAdjustZoom:
    def test_zoom_in_doubles_dimensions(self, rgb_image):
        zoomed = adjust_zoom(rgb_image, 2.0)
        assert zoomed.width == 800
        assert zoomed.height == 600

    def test_zoom_out_halves_dimensions(self, rgb_image):
        zoomed = adjust_zoom(rgb_image, 0.5)
        assert zoomed.width == 200
        assert zoomed.height == 150

    def test_zoom_identity_preserves_size(self, rgb_image):
        zoomed = adjust_zoom(rgb_image, 1.0)
        assert zoomed.width == 400
        assert zoomed.height == 300

    def test_fractional_zoom(self, rgb_image):
        zoomed = adjust_zoom(rgb_image, 1.5)
        assert zoomed.width == 600
        assert zoomed.height == 450

    def test_none_input_returns_none(self):
        assert adjust_zoom(None, 1.5) is None

    def test_zero_zoom_returns_none(self, rgb_image):
        assert adjust_zoom(rgb_image, 0) is None

    def test_negative_zoom_returns_none(self, rgb_image):
        assert adjust_zoom(rgb_image, -1.0) is None

    def test_returns_pil_image(self, rgb_image):
        from PIL import Image
        zoomed = adjust_zoom(rgb_image, 1.0)
        assert isinstance(zoomed, Image.Image)
