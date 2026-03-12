"""
Tests for tag_writer.file_utils — get_image_files and backup_file.
read_metadata requires a live ExifTool process and is covered in integration tests.
"""

import os

import pytest

from tag_writer.file_utils import get_image_files, backup_file


# ---------------------------------------------------------------------------
# get_image_files
# ---------------------------------------------------------------------------

class TestGetImageFiles:
    def test_returns_only_image_files(self, image_directory):
        files = get_image_files(image_directory)
        from tag_writer.constants import IMAGE_EXTENSIONS
        for f in files:
            _, ext = os.path.splitext(f)
            assert ext.lower() in IMAGE_EXTENSIONS, \
                f"Non-image file leaked through: {f}"

    def test_excludes_text_files(self, image_directory):
        files = get_image_files(image_directory)
        basenames = {os.path.basename(f) for f in files}
        assert "document.txt" not in basenames
        assert "notes.pdf" not in basenames

    def test_finds_all_expected_images(self, image_directory):
        files = get_image_files(image_directory)
        basenames = {os.path.basename(f) for f in files}
        for expected in ("photo_a.jpg", "photo_b.jpeg", "photo_c.png", "photo_d.tif"):
            assert expected in basenames, f"Expected image {expected!r} not found"

    def test_returns_sorted_case_insensitive_order(self, image_directory):
        files = get_image_files(image_directory)
        basenames = [os.path.basename(f).lower() for f in files]
        assert basenames == sorted(basenames)

    def test_returns_absolute_paths(self, image_directory):
        files = get_image_files(image_directory)
        for f in files:
            assert os.path.isabs(f), f"Expected absolute path, got: {f}"

    def test_nonexistent_directory_returns_empty(self):
        assert get_image_files("/no/such/dir") == []

    def test_none_returns_empty(self):
        assert get_image_files(None) == []

    def test_empty_directory_returns_empty(self, tmp_path):
        assert get_image_files(str(tmp_path)) == []

    def test_directory_with_only_non_images_returns_empty(self, tmp_path):
        (tmp_path / "readme.txt").write_text("text")
        (tmp_path / "data.csv").write_text("a,b,c")
        assert get_image_files(str(tmp_path)) == []

    def test_case_insensitive_extension_matching(self, tmp_path):
        """Files like .JPG and .PNG should be found regardless of case."""
        from PIL import Image
        upper_jpg = tmp_path / "UPPER.JPG"
        img = Image.new("RGB", (10, 10))
        img.save(str(upper_jpg), format="JPEG")

        files = get_image_files(str(tmp_path))
        basenames = {os.path.basename(f) for f in files}
        assert "UPPER.JPG" in basenames


# ---------------------------------------------------------------------------
# backup_file
# ---------------------------------------------------------------------------

class TestBackupFile:
    def test_creates_backup_file(self, tmp_path):
        original = tmp_path / "photo.jpg"
        original.write_bytes(b"JPEG data")
        backup = backup_file(str(original))
        assert backup is not None
        assert os.path.exists(backup)

    def test_backup_has_same_content(self, tmp_path):
        original = tmp_path / "photo.jpg"
        original.write_bytes(b"test content 123")
        backup = backup_file(str(original))
        assert open(backup, "rb").read() == b"test content 123"

    def test_backup_name_contains_backup_keyword(self, tmp_path):
        original = tmp_path / "photo.jpg"
        original.write_bytes(b"data")
        backup = backup_file(str(original))
        assert "backup" in os.path.basename(backup).lower()

    def test_original_file_untouched(self, tmp_path):
        original = tmp_path / "photo.jpg"
        original.write_bytes(b"original bytes")
        backup_file(str(original))
        assert original.read_bytes() == b"original bytes"

    def test_nonexistent_file_returns_none(self):
        assert backup_file("/no/such/file.jpg") is None

    def test_successive_backups_have_unique_names(self, tmp_path):
        original = tmp_path / "photo.jpg"
        original.write_bytes(b"data")
        b1 = backup_file(str(original))
        b2 = backup_file(str(original))
        assert b1 != b2
        assert os.path.exists(b1)
        assert os.path.exists(b2)

    def test_backup_not_same_path_as_original(self, tmp_path):
        original = tmp_path / "photo.jpg"
        original.write_bytes(b"data")
        backup = backup_file(str(original))
        assert backup != str(original)
