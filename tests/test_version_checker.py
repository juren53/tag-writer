"""
Tests for GitHubVersionChecker — pure-logic methods (no network calls).
"""

import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from github_version_checker import GitHubVersionChecker


@pytest.fixture
def checker():
    return GitHubVersionChecker("juren53/tag-writer", "0.2.3")


# ---------------------------------------------------------------------------
# _normalize_repo_url
# ---------------------------------------------------------------------------

class TestNormalizeRepoUrl:
    def test_short_owner_repo_form(self, checker):
        assert checker._normalize_repo_url("owner/repo") == "owner/repo"

    def test_full_https_github_url(self, checker):
        assert checker._normalize_repo_url("https://github.com/owner/repo") == "owner/repo"

    def test_github_url_with_git_suffix(self, checker):
        assert checker._normalize_repo_url("https://github.com/owner/repo.git") == "owner/repo"

    def test_github_url_with_trailing_slash(self, checker):
        result = checker._normalize_repo_url("https://github.com/owner/repo/")
        assert result == "owner/repo"

    def test_no_slash_raises_value_error(self, checker):
        with pytest.raises(ValueError):
            checker._normalize_repo_url("notaurl")

    def test_tag_writer_repo(self, checker):
        assert checker._normalize_repo_url("juren53/tag-writer") == "juren53/tag-writer"


# ---------------------------------------------------------------------------
# compare_versions
# ---------------------------------------------------------------------------

class TestCompareVersions:
    def test_equal_versions(self, checker):
        assert checker.compare_versions("0.2.3", "0.2.3") == 0

    def test_equal_with_v_prefix(self, checker):
        assert checker.compare_versions("v0.2.3", "0.2.3") == 0

    def test_older_patch(self, checker):
        assert checker.compare_versions("0.2.3", "0.2.4") == -1

    def test_newer_patch(self, checker):
        assert checker.compare_versions("0.2.4", "0.2.3") == 1

    def test_older_minor(self, checker):
        assert checker.compare_versions("0.1.9", "0.2.0") == -1

    def test_newer_minor(self, checker):
        assert checker.compare_versions("0.3.0", "0.2.9") == 1

    def test_older_major(self, checker):
        assert checker.compare_versions("0.9.9", "1.0.0") == -1

    def test_newer_major(self, checker):
        assert checker.compare_versions("1.0.0", "0.9.9") == 1

    def test_prerelease_less_than_release(self, checker):
        # "0.2.3a" is a point-release/patch label → less than clean "0.2.3"
        assert checker.compare_versions("0.2.3a", "0.2.3") == -1

    def test_release_greater_than_prerelease(self, checker):
        assert checker.compare_versions("0.2.3", "0.2.3a") == 1

    def test_alpha_less_than_beta(self, checker):
        assert checker.compare_versions("0.2.3a", "0.2.3b") == -1

    def test_beta_greater_than_alpha(self, checker):
        assert checker.compare_versions("0.2.3b", "0.2.3a") == 1

    def test_patch_ten_greater_than_patch_nine(self, checker):
        assert checker.compare_versions("0.2.10", "0.2.9") == 1

    def test_two_part_version_comparison(self, checker):
        assert checker.compare_versions("0.2", "0.3") == -1
        assert checker.compare_versions("0.3", "0.2") == 1

    def test_three_zeros_equal(self, checker):
        assert checker.compare_versions("0.0.0", "0.0.0") == 0

    def test_symmetry(self, checker):
        """compare(a, b) == -compare(b, a) for unequal versions."""
        pairs = [
            ("0.2.3", "0.2.4"),
            ("0.1.0", "0.2.0"),
            ("0.2.3a", "0.2.3"),
        ]
        for v1, v2 in pairs:
            assert checker.compare_versions(v1, v2) == -checker.compare_versions(v2, v1)


# ---------------------------------------------------------------------------
# VersionCheckResult defaults
# ---------------------------------------------------------------------------

def test_version_check_result_defaults():
    from github_version_checker import VersionCheckResult
    r = VersionCheckResult()
    assert r.has_update is False
    assert r.is_newer is False
    assert r.error_message == ""
    assert r.current_version == ""
    assert r.latest_version == ""
