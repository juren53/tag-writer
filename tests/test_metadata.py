"""
Tests for MetadataManager — in-memory field operations, sanitize, process, and JSON I/O.
ExifTool file I/O (load_from_file, save_to_file) is exercised separately via integration tests.
"""

import json
import os

import pytest

from tag_writer.metadata import MetadataManager


@pytest.fixture
def mgr():
    return MetadataManager()


# ---------------------------------------------------------------------------
# Basic field operations
# ---------------------------------------------------------------------------

class TestFieldOperations:
    def test_get_field_default_empty_string(self, mgr):
        assert mgr.get_field("Headline") == ""

    def test_get_field_custom_default(self, mgr):
        assert mgr.get_field("Headline", default="N/A") == "N/A"

    def test_set_and_get_field(self, mgr):
        mgr.set_field("Headline", "Breaking News")
        assert mgr.get_field("Headline") == "Breaking News"

    def test_overwrite_field(self, mgr):
        mgr.set_field("Credit", "AP")
        mgr.set_field("Credit", "Reuters")
        assert mgr.get_field("Credit") == "Reuters"

    def test_clear_empties_metadata(self, mgr):
        mgr.set_field("Headline", "Test")
        mgr.set_field("Credit", "Wire")
        mgr.clear()
        assert mgr.metadata == {}

    def test_clear_makes_get_return_default(self, mgr):
        mgr.set_field("Headline", "Test")
        mgr.clear()
        assert mgr.get_field("Headline") == ""

    def test_get_field_names_count(self, mgr):
        assert len(mgr.get_field_names()) == 12

    def test_get_field_names_contains_expected(self, mgr):
        names = mgr.get_field_names()
        for expected in ("Headline", "Caption-Abstract", "By-line",
                         "Credit", "CopyrightNotice", "DateCreated"):
            assert expected in names, f"{expected!r} missing from field_names"


# ---------------------------------------------------------------------------
# _sanitize_value
# ---------------------------------------------------------------------------

class TestSanitizeValue:
    def test_strips_leading_trailing_whitespace(self, mgr):
        assert mgr._sanitize_value("  hello  ") == "hello"

    def test_removes_null_bytes(self, mgr):
        assert mgr._sanitize_value("hel\x00lo") == "hello"

    def test_normalizes_crlf_to_lf(self, mgr):
        assert mgr._sanitize_value("line1\r\nline2") == "line1\nline2"

    def test_normalizes_bare_cr_to_lf(self, mgr):
        assert mgr._sanitize_value("line1\rline2") == "line1\nline2"

    def test_truncates_at_2000_chars(self, mgr):
        long_str = "x" * 3000
        result = mgr._sanitize_value(long_str)
        assert len(result) == 2000

    def test_short_value_unchanged(self, mgr):
        assert mgr._sanitize_value("short") == "short"

    def test_empty_string_unchanged(self, mgr):
        assert mgr._sanitize_value("") == ""

    def test_non_string_passthrough(self, mgr):
        assert mgr._sanitize_value(42) == 42
        assert mgr._sanitize_value(None) is None


# ---------------------------------------------------------------------------
# _process_metadata — field priority / mapping
# ---------------------------------------------------------------------------

class TestProcessMetadata:
    def test_iptc_headline_recognized(self, mgr):
        raw = {"IPTC:Headline": "Test Story"}
        result = mgr._process_metadata(raw)
        assert result["Headline"] == "Test Story"

    def test_xmp_headline_fallback(self, mgr):
        raw = {"XMP-photoshop:Headline": "XMP Headline"}
        result = mgr._process_metadata(raw)
        assert result["Headline"] == "XMP Headline"

    def test_iptc_takes_priority_over_xmp(self, mgr):
        raw = {
            "IPTC:Headline": "IPTC wins",
            "XMP-photoshop:Headline": "XMP loses",
        }
        result = mgr._process_metadata(raw)
        assert result["Headline"] == "IPTC wins"

    def test_by_line_from_iptc(self, mgr):
        raw = {"IPTC:By-line": "Jane Doe"}
        result = mgr._process_metadata(raw)
        assert result["By-line"] == "Jane Doe"

    def test_by_line_xmp_fallback(self, mgr):
        raw = {"XMP:Creator": "John Smith"}
        result = mgr._process_metadata(raw)
        assert result["By-line"] == "John Smith"

    def test_copyright_from_iptc(self, mgr):
        raw = {"IPTC:CopyrightNotice": "© 2024"}
        result = mgr._process_metadata(raw)
        assert result["CopyrightNotice"] == "© 2024"

    def test_date_modified_from_exif_modify_date(self, mgr):
        raw = {"EXIF:ModifyDate": "2024:01:15 10:30:00"}
        result = mgr._process_metadata(raw)
        assert result["DateModified"] == "2024:01:15 10:30:00"

    def test_date_modified_xmp_fallback(self, mgr):
        raw = {"XMP:ModifyDate": "2024:06:01 08:00:00"}
        result = mgr._process_metadata(raw)
        assert result["DateModified"] == "2024:06:01 08:00:00"

    def test_missing_field_not_in_result(self, mgr):
        raw = {"IPTC:Headline": "Only headline"}
        result = mgr._process_metadata(raw)
        assert "By-line" not in result

    def test_empty_raw_returns_empty_dict(self, mgr):
        result = mgr._process_metadata({})
        assert result == {}

    def test_caption_abstract_from_iptc(self, mgr):
        raw = {"IPTC:Caption-Abstract": "A photo caption"}
        result = mgr._process_metadata(raw)
        assert result["Caption-Abstract"] == "A photo caption"

    def test_source_from_iptc(self, mgr):
        raw = {"IPTC:Source": "AP"}
        result = mgr._process_metadata(raw)
        assert result["Source"] == "AP"


# ---------------------------------------------------------------------------
# export_to_json / import_from_json
# ---------------------------------------------------------------------------

class TestJsonExport:
    def test_export_creates_file(self, mgr, tmp_path):
        mgr.set_field("Headline", "Export Test")
        out = str(tmp_path / "export.json")
        assert mgr.export_to_json(out) is True
        assert os.path.exists(out)

    def test_export_is_valid_json(self, mgr, tmp_path):
        mgr.set_field("Headline", "Valid JSON")
        out = str(tmp_path / "export.json")
        mgr.export_to_json(out)
        with open(out) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_export_has_required_keys(self, mgr, tmp_path):
        out = str(tmp_path / "export.json")
        mgr.export_to_json(out)
        with open(out) as f:
            data = json.load(f)
        assert "filename" in data
        assert "export_date" in data
        assert "metadata" in data

    def test_export_includes_set_fields(self, mgr, tmp_path):
        mgr.set_field("Headline", "News")
        mgr.set_field("Credit", "AP")
        out = str(tmp_path / "export.json")
        mgr.export_to_json(out)
        with open(out) as f:
            data = json.load(f)
        assert data["metadata"]["Headline"] == "News"
        assert data["metadata"]["Credit"] == "AP"

    def test_export_bad_path_returns_false(self, mgr):
        result = mgr.export_to_json("/nonexistent_dir/cannot_create.json")
        assert result is False


class TestJsonImport:
    def test_import_restores_fields(self, tmp_path):
        import_data = {"metadata": {"Headline": "Imported", "Credit": "Reuters"}}
        f = tmp_path / "import.json"
        f.write_text(json.dumps(import_data))

        m = MetadataManager()
        assert m.import_from_json(str(f)) is True
        assert m.get_field("Headline") == "Imported"
        assert m.get_field("Credit") == "Reuters"

    def test_import_ignores_unknown_fields(self, tmp_path):
        import_data = {"metadata": {"Headline": "OK", "UnknownField": "skip me"}}
        f = tmp_path / "import.json"
        f.write_text(json.dumps(import_data))

        m = MetadataManager()
        m.import_from_json(str(f))
        assert m.get_field("Headline") == "OK"
        assert "UnknownField" not in m.metadata

    def test_import_flat_json_without_wrapper(self, tmp_path):
        import_data = {"Headline": "Flat"}
        f = tmp_path / "flat.json"
        f.write_text(json.dumps(import_data))

        m = MetadataManager()
        m.import_from_json(str(f))
        assert m.get_field("Headline") == "Flat"

    def test_import_missing_file_returns_false(self, mgr):
        assert mgr.import_from_json("/no/such/file.json") is False

    def test_roundtrip_preserves_all_set_fields(self, tmp_path):
        m1 = MetadataManager()
        m1.set_field("Headline", "Roundtrip")
        m1.set_field("By-line", "J. Smith")
        m1.set_field("CopyrightNotice", "© 2024")

        out = str(tmp_path / "roundtrip.json")
        m1.export_to_json(out)

        m2 = MetadataManager()
        m2.import_from_json(out)
        assert m2.get_field("Headline") == "Roundtrip"
        assert m2.get_field("By-line") == "J. Smith"
        assert m2.get_field("CopyrightNotice") == "© 2024"
