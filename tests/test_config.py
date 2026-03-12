"""
Tests for tag_writer.config — Config class save/load and recent-file/dir management.
"""

import json
import os

import pytest

from tag_writer.config import Config


class TestConfigDefaults:
    def test_no_selected_file(self, fresh_config):
        assert fresh_config.selected_file is None

    def test_empty_recent_files(self, fresh_config):
        assert fresh_config.recent_files == []

    def test_empty_recent_directories(self, fresh_config):
        assert fresh_config.recent_directories == []

    def test_default_current_file_index(self, fresh_config):
        assert fresh_config.current_file_index == -1

    def test_default_zoom_factor(self, fresh_config):
        assert fresh_config.ui_zoom_factor == 1.0

    def test_default_dark_mode_off(self, fresh_config):
        assert fresh_config.dark_mode is False

    def test_auto_check_updates_off(self, fresh_config):
        assert fresh_config.auto_check_updates is False


class TestConfigSaveLoad:
    def test_config_file_created_on_save(self, fresh_config):
        fresh_config.save_config()
        assert os.path.exists(fresh_config.config_file)

    def test_config_file_is_valid_json(self, fresh_config):
        fresh_config.save_config()
        with open(fresh_config.config_file) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_config_file_has_required_keys(self, fresh_config):
        fresh_config.save_config()
        with open(fresh_config.config_file) as f:
            data = json.load(f)
        for key in ("recent_files", "recent_directories", "dark_mode",
                    "ui_zoom_factor", "current_theme"):
            assert key in data, f"Missing key {key!r} in config JSON"

    def test_roundtrip_dark_mode(self, config_dir):
        c1 = Config()
        c1.dark_mode = True
        c1.save_config()

        c2 = Config()
        assert c2.dark_mode is True

    def test_roundtrip_zoom_factor(self, config_dir):
        c1 = Config()
        c1.ui_zoom_factor = 1.5
        c1.save_config()

        c2 = Config()
        assert c2.ui_zoom_factor == 1.5

    def test_roundtrip_current_theme(self, config_dir):
        c1 = Config()
        c1.current_theme = "Solarized"
        c1.save_config()

        c2 = Config()
        assert c2.current_theme == "Solarized"

    def test_roundtrip_auto_check_updates(self, config_dir):
        c1 = Config()
        c1.auto_check_updates = True
        c1.save_config()

        c2 = Config()
        assert c2.auto_check_updates is True

    def test_roundtrip_skipped_versions(self, config_dir):
        c1 = Config()
        c1.skipped_versions = ["0.2.1", "0.2.2"]
        c1.save_config()

        c2 = Config()
        assert c2.skipped_versions == ["0.2.1", "0.2.2"]


class TestRecentFiles:
    def test_add_existing_file(self, fresh_config, tmp_path):
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"fake jpeg")
        fresh_config.add_recent_file(str(f))
        assert str(f) in fresh_config.recent_files

    def test_added_file_is_first(self, fresh_config, tmp_path):
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"x")
        fresh_config.add_recent_file(str(f))
        assert fresh_config.recent_files[0] == str(f)

    def test_nonexistent_file_ignored(self, fresh_config):
        fresh_config.add_recent_file("/does/not/exist.jpg")
        assert "/does/not/exist.jpg" not in fresh_config.recent_files

    def test_none_ignored(self, fresh_config):
        fresh_config.add_recent_file(None)
        assert fresh_config.recent_files == []

    def test_duplicate_moves_to_front(self, fresh_config, tmp_path):
        f1 = tmp_path / "a.jpg"
        f2 = tmp_path / "b.jpg"
        f1.write_bytes(b"x")
        f2.write_bytes(b"x")

        fresh_config.add_recent_file(str(f1))
        fresh_config.add_recent_file(str(f2))
        fresh_config.add_recent_file(str(f1))  # re-add f1

        assert fresh_config.recent_files[0] == str(f1)
        assert fresh_config.recent_files.count(str(f1)) == 1

    def test_capped_at_five(self, fresh_config, tmp_path):
        for i in range(7):
            f = tmp_path / f"file{i}.jpg"
            f.write_bytes(b"x")
            fresh_config.add_recent_file(str(f))
        assert len(fresh_config.recent_files) <= 5


class TestRecentDirectories:
    def test_add_existing_directory(self, fresh_config, tmp_path):
        sub = tmp_path / "photos"
        sub.mkdir()
        fresh_config.add_recent_directory(str(sub))
        assert str(sub) in fresh_config.recent_directories

    def test_nonexistent_dir_ignored(self, fresh_config):
        fresh_config.add_recent_directory("/no/such/dir")
        assert "/no/such/dir" not in fresh_config.recent_directories

    def test_file_path_ignored(self, fresh_config, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        fresh_config.add_recent_directory(str(f))
        assert str(f) not in fresh_config.recent_directories

    def test_duplicate_moves_to_front(self, fresh_config, tmp_path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()

        fresh_config.add_recent_directory(str(d1))
        fresh_config.add_recent_directory(str(d2))
        fresh_config.add_recent_directory(str(d1))

        assert fresh_config.recent_directories[0] == str(d1)
        assert fresh_config.recent_directories.count(str(d1)) == 1

    def test_capped_at_five(self, fresh_config, tmp_path):
        for i in range(7):
            d = tmp_path / f"dir{i}"
            d.mkdir()
            fresh_config.add_recent_directory(str(d))
        assert len(fresh_config.recent_directories) <= 5
