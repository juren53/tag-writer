"""
Regression tests — one test class per notable past bug fix.
Each class documents the version it was fixed in and the original symptom.
"""

import os
import sys

import pytest

# ---------------------------------------------------------------------------
# v0.1.8 — Path traversal protection in file rename
#
# Symptom: user could type "../secret.jpg" in rename dialog and write outside
# the current directory.  Fix: run new_filename through os.path.basename()
# and reject '.', '..', empty strings, and names containing null bytes.
# ---------------------------------------------------------------------------

def _sanitize_rename(raw_input: str):
    """
    Mirror of the validation logic in FileOpsMixin.on_rename_file.
    Returns the sanitised filename, or None if the input is invalid.
    """
    new_filename = os.path.basename(raw_input)
    if not new_filename or new_filename in ('.', '..') or '\x00' in new_filename:
        return None
    return new_filename


class TestRenamePathTraversal:
    """v0.1.8 — path traversal protection in the rename dialog."""

    def test_plain_filename_accepted(self):
        assert _sanitize_rename("photo.jpg") == "photo.jpg"

    def test_path_traversal_stripped_to_basename(self):
        result = _sanitize_rename("../secret.jpg")
        assert result == "secret.jpg"

    def test_deep_path_traversal_stripped(self):
        result = _sanitize_rename("../../etc/passwd")
        assert result == "passwd"

    def test_absolute_path_stripped_to_basename(self):
        result = _sanitize_rename("/tmp/evil.jpg")
        assert result == "evil.jpg"

    def test_dot_rejected(self):
        assert _sanitize_rename(".") is None

    def test_dotdot_rejected(self):
        assert _sanitize_rename("..") is None

    def test_empty_string_rejected(self):
        assert _sanitize_rename("") is None

    def test_null_byte_rejected(self):
        assert _sanitize_rename("photo\x00.jpg") is None

    def test_filename_with_extension_preserved(self):
        assert _sanitize_rename("IMG_1234.jpg") == "IMG_1234.jpg"

    def test_windows_style_path_stripped(self):
        result = _sanitize_rename(r"C:\Users\test\photo.jpg")
        assert result == "photo.jpg"


# ---------------------------------------------------------------------------
# v0.1.8 — Metadata value sanitization (_sanitize_value)
#
# Symptom: writing metadata containing null bytes or bare \r caused ExifTool
# errors or corrupt fields.  Also, values >2000 chars could exceed IPTC limits.
# Fix: _sanitize_value() added to MetadataManager.
# ---------------------------------------------------------------------------

class TestMetadataSanitizationRegression:
    """v0.1.8 — _sanitize_value strips unsafe characters before ExifTool writes."""

    @pytest.fixture
    def mgr(self):
        from tag_writer.metadata import MetadataManager
        return MetadataManager()

    def test_null_byte_in_caption_stripped(self, mgr):
        result = mgr._sanitize_value("Caption\x00 text")
        assert "\x00" not in result

    def test_multiple_null_bytes_all_stripped(self, mgr):
        result = mgr._sanitize_value("\x00\x00hello\x00")
        assert result == "hello"

    def test_windows_line_endings_normalised(self, mgr):
        result = mgr._sanitize_value("line1\r\nline2\r\nline3")
        assert "\r" not in result
        assert result == "line1\nline2\nline3"

    def test_iptc_value_over_2000_chars_truncated(self, mgr):
        assert len(mgr._sanitize_value("x" * 2500)) == 2000

    def test_exactly_2000_chars_not_truncated(self, mgr):
        assert len(mgr._sanitize_value("x" * 2000)) == 2000

    def test_leading_whitespace_stripped(self, mgr):
        assert mgr._sanitize_value("   text") == "text"

    def test_trailing_whitespace_stripped(self, mgr):
        assert mgr._sanitize_value("text   ") == "text"


# ---------------------------------------------------------------------------
# v0.0.7 — DateModified field fallback chain
#
# Symptom: DateModified showed blank when EXIF:ModifyDate was absent; later
# versions added FileModifyDate → XMP:ModifyDate → ICC_Profile:ProfileDateTime
# as fallbacks (in that priority order).
# ---------------------------------------------------------------------------

class TestDateModifiedFallbackChain:
    """v0.0.7+ — DateModified uses a 4-tier fallback chain."""

    @pytest.fixture
    def mgr(self):
        from tag_writer.metadata import MetadataManager
        return MetadataManager()

    def test_exif_modify_date_is_first_priority(self, mgr):
        raw = {
            "EXIF:ModifyDate": "2024:01:01 00:00:00",
            "EXIF:FileModifyDate": "2024:06:01 00:00:00",
            "XMP:ModifyDate": "2024:12:01 00:00:00",
        }
        result = mgr._process_metadata(raw)
        assert result["DateModified"] == "2024:01:01 00:00:00"

    def test_file_modify_date_fallback(self, mgr):
        raw = {"EXIF:FileModifyDate": "2024:06:01 00:00:00"}
        result = mgr._process_metadata(raw)
        assert result["DateModified"] == "2024:06:01 00:00:00"

    def test_xmp_modify_date_fallback(self, mgr):
        raw = {"XMP:ModifyDate": "2024:09:01 12:00:00"}
        result = mgr._process_metadata(raw)
        assert result["DateModified"] == "2024:09:01 12:00:00"

    def test_icc_profile_datetime_fallback(self, mgr):
        raw = {"ICC_Profile:ProfileDateTime": "2024:03:15 08:00:00"}
        result = mgr._process_metadata(raw)
        assert result["DateModified"] == "2024:03:15 08:00:00"

    def test_no_date_fields_yields_no_key(self, mgr):
        raw = {"IPTC:Headline": "No dates here"}
        result = mgr._process_metadata(raw)
        assert "DateModified" not in result


# ---------------------------------------------------------------------------
# v0.1.8 — get_image_files excludes symlinks (follow_symlinks=False)
#
# Symptom: on Linux, dangling symlinks in a photo directory would cause an
# exception when os.listdir()+os.path.isfile() was called.  Fix: switched to
# os.scandir() with entry.is_file(follow_symlinks=False).
# ---------------------------------------------------------------------------

class TestGetImageFilesSymlinks:
    """v0.1.8 — get_image_files uses scandir with follow_symlinks=False."""

    def test_real_images_still_returned(self, image_directory):
        from tag_writer.file_utils import get_image_files
        files = get_image_files(image_directory)
        assert len(files) > 0

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")
    def test_symlinks_not_included(self, tmp_path):
        from PIL import Image
        from tag_writer.file_utils import get_image_files

        real = tmp_path / "real.jpg"
        Image.new("RGB", (10, 10)).save(str(real), format="JPEG")

        link = tmp_path / "link.jpg"
        link.symlink_to(real)

        files = get_image_files(str(tmp_path))
        basenames = {os.path.basename(f) for f in files}
        # The symlink should not appear — only the real file
        assert "link.jpg" not in basenames
        assert "real.jpg" in basenames


# ---------------------------------------------------------------------------
# v0.1.4 — 16-bit TIFF image normalisation
#
# Symptom: opening a 16-bit grayscale TIFF raised an error / showed a black
# image because PIL's mode 'I;16' can't be displayed directly.
# Fix: load_image() detects mode 'I;16'/'I;16B' and normalises to 8-bit.
# ---------------------------------------------------------------------------

try:
    import numpy as _np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required for 16-bit TIFF tests")
class TestSixteenBitTiffLoading:
    """v0.1.4 — 16-bit grayscale TIFFs are normalised to 8-bit for display."""

    def _make_16bit_tiff(self, tmp_path, name, data):
        """Save a uint16 numpy array as a 16-bit TIFF and return the path."""
        from PIL import Image
        # fromarray with uint16 data creates mode 'I;16' — the exact mode
        # that triggered the original display bug — without using the
        # deprecated `mode=` parameter.
        img = Image.fromarray(data)
        path = str(tmp_path / name)
        img.save(path, format="TIFF")
        return path

    def test_16bit_tiff_loads_without_error(self, tmp_path):
        import numpy as np
        from tag_writer.image_utils import load_image

        data = np.linspace(0, 65535, 100 * 80, dtype=np.uint16).reshape(80, 100)
        tiff_path = self._make_16bit_tiff(tmp_path, "test_16bit.tif", data)

        result = load_image(tiff_path)
        assert result is not None

    def test_16bit_tiff_result_is_displayable(self, tmp_path):
        import numpy as np
        from tag_writer.image_utils import load_image

        data = np.linspace(0, 65535, 100 * 80, dtype=np.uint16).reshape(80, 100)
        tiff_path = self._make_16bit_tiff(tmp_path, "test_16bit.tif", data)

        result = load_image(tiff_path)
        # After loading, the image must be in a displayable 8-bit mode
        assert result.mode in ("L", "RGB", "RGBA")

    def test_16bit_tiff_uniform_image_does_not_crash(self, tmp_path):
        """Edge case: uniform (all-same-value) image has ptp=0, must not divide by zero."""
        import numpy as np
        from tag_writer.image_utils import load_image

        data = np.full((80, 100), 32768, dtype=np.uint16)
        tiff_path = self._make_16bit_tiff(tmp_path, "uniform_16bit.tif", data)

        result = load_image(tiff_path)
        assert result is not None
