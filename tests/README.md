# Tag Writer — Test Suite

## Overview

Pytest-based unit and regression test suite for the non-GUI logic of Tag Writer.
All tests run without launching the Qt application and without a live ExifTool process.

**Run all tests:**
```
python -m pytest tests/
```

**Run a single file:**
```
python -m pytest tests/test_metadata.py -v
```

---

## Test Files

### `conftest.py` — Shared Fixtures

Adds `src/` to `sys.path` and provides fixtures used across multiple test files.

| Fixture | What it creates |
|---------|----------------|
| `sample_jpeg(tmp_path)` | 100×80 RGB JPEG in a temp directory |
| `sample_png(tmp_path)` | 60×40 RGB PNG in a temp directory |
| `image_directory(tmp_path)` | Temp dir with 4 images + 2 non-images (txt, pdf) |
| `config_dir(tmp_path, monkeypatch)` | Patches `os.path.expanduser` so Config uses `tmp_path` instead of `~` |
| `fresh_config(config_dir)` | A clean `Config()` instance backed by a temp directory |

---

### `test_constants.py` — Constants (10 tests)

Verifies the values and format of `src/tag_writer/constants.py`.

- `APP_NAME` and `APP_ORGANIZATION` match expected strings
- `APP_VERSION` is at least `major.minor` format
- `APP_USER_MODEL_ID` contains `APP_VERSION`
- `GITHUB_REPO` is `owner/repo` format
- `IMAGE_EXTENSIONS` includes `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`
- All extensions are lowercase and start with `.`
- `EXIFTOOL_TIMEOUT` is positive
- `APP_TIMESTAMP` is non-empty

---

### `test_config.py` — Config Class (26 tests)

Tests `Config` save/load and recent-file/directory management.
The `fresh_config` fixture redirects all file I/O to a `tmp_path` so the user's
real `~/.tag_writer_config.json` is never touched.

**TestConfigDefaults**
- All default values (`selected_file`, `recent_files`, `ui_zoom_factor`, etc.)

**TestConfigSaveLoad**
- Config file is created on `save_config()`
- File contains valid JSON with all required keys
- Roundtrip tests: `dark_mode`, `ui_zoom_factor`, `current_theme`, `auto_check_updates`, `skipped_versions`

**TestRecentFiles**
- Added file appears first in the list
- Non-existent files and `None` are silently ignored
- Duplicate re-adds move the entry to the front (no duplicates)
- List is capped at 5 entries

**TestRecentDirectories**
- Same deduplication and cap-at-5 behaviour as recent files
- File paths (not directories) are rejected

---

### `test_metadata.py` — MetadataManager (40 tests)

Tests `MetadataManager` in-memory operations. No ExifTool process is needed.
ExifTool I/O (`load_from_file`, `save_to_file`) is excluded — those require
a live ExifTool and belong in integration tests.

**TestFieldOperations**
- `get_field` returns `""` by default, or a custom default
- `set_field` / `get_field` roundtrip
- `clear()` empties `metadata` dict
- `get_field_names()` returns all 12 defined fields

**TestSanitizeValue**
- Strips leading/trailing whitespace
- Removes null bytes (`\x00`)
- Normalises `\r\n` and bare `\r` to `\n`
- Truncates values > 2000 characters (IPTC limit)
- Passes non-string values (int, None) through unchanged

**TestProcessMetadata**
- IPTC fields recognised (Headline, By-line, Caption-Abstract, Source, Copyright)
- XMP fields used as fallback when IPTC is absent
- IPTC takes priority when both IPTC and XMP are present
- DateModified uses EXIF:ModifyDate first, XMP:ModifyDate as fallback
- Fields absent from raw metadata are absent from the result

**TestJsonExport**
- `export_to_json()` creates the file and returns `True`
- Output is valid JSON with keys `filename`, `export_date`, `metadata`
- Set fields appear in `metadata`
- Bad path returns `False`

**TestJsonImport**
- `import_from_json()` restores fields from a `{"metadata": {...}}` wrapper
- Also handles flat JSON (no `metadata` wrapper)
- Unknown fields are silently ignored
- Missing file returns `False`
- Full export → import roundtrip preserves all set fields

---

### `test_file_utils.py` — File Utilities (17 tests)

Tests `get_image_files` and `backup_file` from `src/tag_writer/file_utils.py`.
`read_metadata` requires ExifTool and is not tested here.

**TestGetImageFiles**
- Returns only files with recognised image extensions
- Excludes `.txt`, `.pdf`, and other non-images
- Finds all expected images in the fixture directory
- Returns entries sorted case-insensitively by filename
- Returns absolute paths
- Returns `[]` for non-existent directory, `None`, and empty directory
- Case-insensitive extension matching (e.g. `.JPG`)

**TestBackupFile**
- Backup file is created and has identical content to the original
- Backup filename contains the word "backup"
- Original file is not modified
- Non-existent source returns `None`
- Two successive backups get unique names (counter suffix)
- Backup path differs from the original path

---

### `test_image_utils.py` — Image Processing (15 tests)

Tests the PIL-based helpers in `src/tag_writer/image_utils.py`.
`pil_to_pixmap` is Qt-dependent and is not tested here.
The entire module is skipped if Pillow is not installed.

**TestCreateThumbnail**
- Returns a PIL Image
- Resulting width and height are within `max_size`
- Aspect ratio is preserved (within 10% tolerance)
- `None` input returns `None`
- Images smaller than `max_size` are not enlarged

**TestAdjustZoom**
- Zoom 2.0× doubles both dimensions
- Zoom 0.5× halves both dimensions
- Zoom 1.0× is identity
- Fractional zoom (1.5×) is correct
- `None` input, zero zoom, and negative zoom all return `None`
- Returns a PIL Image instance

---

### `test_version_checker.py` — Version Checker (23 tests)

Tests pure-logic methods of `GitHubVersionChecker` from `github_version_checker.py`.
No network calls are made.

**TestNormalizeRepoUrl**
- `"owner/repo"` short form
- `"https://github.com/owner/repo"` full URL
- `.git` suffix stripped
- Trailing slash stripped
- Bare string without `/` raises `ValueError`

**TestCompareVersions**

| Comparison | Expected |
|-----------|----------|
| `"0.2.3"` vs `"0.2.3"` | 0 |
| `"v0.2.3"` vs `"0.2.3"` | 0 (v-prefix stripped) |
| `"0.2.3"` vs `"0.2.4"` | -1 |
| `"0.2.4"` vs `"0.2.3"` | 1 |
| `"0.2.3a"` vs `"0.2.3"` | -1 (prerelease < release) |
| `"0.2.3"` vs `"0.2.3a"` | 1 |
| `"0.2.3a"` vs `"0.2.3b"` | -1 (alpha < beta) |
| `"0.2.10"` vs `"0.2.9"` | 1 (numeric, not lexicographic) |

- Symmetry property: `compare(a,b) == -compare(b,a)` for three unequal pairs
- Two-part version strings work (padded to 3 parts)
- `VersionCheckResult` default field values are sane

---

### `test_regressions.py` — Regression Tests (27 tests)

Named regression tests, one class per past bug. Each class documents the version
it was fixed in and the original symptom.

**TestRenamePathTraversal** *(v0.1.8)*
> Symptom: user could type `../secret.jpg` in the rename dialog and write outside
> the current directory.

Tests the sanitisation logic (`os.path.basename()` + reject `.`, `..`, empty,
null-byte filenames) against:
- Plain filename → accepted unchanged
- `../secret.jpg` → stripped to `secret.jpg`
- `../../etc/passwd` → stripped to `passwd`
- Absolute path → stripped to basename
- `.`, `..`, empty string, null byte → rejected (`None`)
- Windows-style `C:\...\photo.jpg` → stripped to `photo.jpg`

**TestMetadataSanitizationRegression** *(v0.1.8)*
> Symptom: writing metadata with null bytes or bare `\r` caused ExifTool errors
> or corrupt fields. Values > 2000 chars exceeded the IPTC limit.

Confirms `_sanitize_value()` handles each case in isolation.

**TestDateModifiedFallbackChain** *(v0.0.7+)*
> Symptom: `DateModified` showed blank when `EXIF:ModifyDate` was absent.

Verifies the 4-tier priority chain:
`EXIF:ModifyDate` → `EXIF:FileModifyDate` → `XMP:ModifyDate` → `ICC_Profile:ProfileDateTime`

**TestGetImageFilesSymlinks** *(v0.1.8)*
> Symptom: dangling symlinks caused an exception when scanning a directory.

- Real images are still returned
- Symlinks are excluded (`follow_symlinks=False`) — test skipped on Windows
  where creating symlinks requires elevated privileges

**TestSixteenBitTiffLoading** *(v0.1.4)*
> Symptom: opening a 16-bit grayscale TIFF raised an error or showed a black
> image because PIL mode `I;16` cannot be displayed directly.

- 16-bit TIFF loads without raising an exception
- Loaded image is in a displayable 8-bit mode (`L`, `RGB`, or `RGBA`)
- **Edge case:** uniform image (all pixels equal → `ptp = 0`) does not divide
  by zero — this specific path caused a `ZeroDivisionError` before the fix

*Skipped if numpy is not installed.*

---

## Dependencies

All test dependencies are already present in `requirements.txt` plus `pytest`:

```
pip install pytest
```

No additional packages are required. The test suite uses only:
- `pytest` — test runner and fixtures
- `Pillow` — creating test images (already a project dependency)
- `numpy` — 16-bit TIFF regression tests only (skipped if absent)

---

## What Is Not Tested Here

| Area | Reason | How to test |
|------|--------|-------------|
| `load_from_file` / `save_to_file` | Requires a live ExifTool process | Integration test with `tools/exiftool.exe` |
| `read_metadata` in `file_utils.py` | Requires ExifTool | Integration test |
| `pil_to_pixmap` | Requires a Qt display | Qt-based integration test |
| All GUI mixins (`MenuMixin`, `WindowMixin`, etc.) | Require a Qt `QApplication` | Manual / Qt UI test framework (e.g. pytest-qt) |
| `SingleInstanceChecker` | File-locking behaviour is process-level | Manual or subprocess-based test |
| `ThemeManager.generate_stylesheet` | Requires `QColor` (Qt) | Qt-based test |
| GitHub network calls in `UpdatesMixin` | Require network and GitHub API | Mocked integration test |
