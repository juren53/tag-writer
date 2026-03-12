"""
Tests for tag_writer.constants module.
"""

from tag_writer.constants import (
    APP_NAME,
    APP_VERSION,
    APP_TIMESTAMP,
    APP_ORGANIZATION,
    APP_USER_MODEL_ID,
    GITHUB_REPO,
    IMAGE_EXTENSIONS,
    EXIFTOOL_TIMEOUT,
)


def test_app_name():
    assert APP_NAME == "Tag Writer"


def test_app_organization():
    assert APP_ORGANIZATION == "SynchroSoft"


def test_app_version_format():
    """Version should be at least major.minor (e.g. 0.2 or 0.2.3)."""
    parts = APP_VERSION.split(".")
    assert len(parts) >= 2
    assert parts[0].isdigit()
    assert parts[1].isdigit()


def test_app_user_model_id_contains_version():
    assert APP_VERSION in APP_USER_MODEL_ID


def test_github_repo_format():
    assert "/" in GITHUB_REPO
    owner, repo = GITHUB_REPO.split("/", 1)
    assert owner
    assert repo


def test_image_extensions_includes_common_formats():
    for ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
        assert ext in IMAGE_EXTENSIONS, f"Expected {ext!r} in IMAGE_EXTENSIONS"


def test_image_extensions_are_lowercase():
    for ext in IMAGE_EXTENSIONS:
        assert ext == ext.lower(), f"Extension {ext!r} must be lowercase"


def test_image_extensions_have_leading_dot():
    for ext in IMAGE_EXTENSIONS:
        assert ext.startswith("."), f"Extension {ext!r} must start with '.'"


def test_exiftool_timeout_is_positive():
    assert EXIFTOOL_TIMEOUT > 0


def test_app_timestamp_not_empty():
    assert APP_TIMESTAMP.strip()
