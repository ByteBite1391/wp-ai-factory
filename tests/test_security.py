import os
import pytest
from core.security import safe_join, SecurityError


@pytest.fixture
def root(tmp_path):
    return str(tmp_path)


def test_safe_join_valid(root):
    result = safe_join(root, "wp-content/themes/x/style.css")
    assert result.startswith(root)
    assert result.endswith("style.css")


def test_safe_join_root_file(root):
    result = safe_join(root, "readme.txt")
    assert result.endswith("readme.txt")


def test_safe_join_rejects_parent_escape(root):
    with pytest.raises(SecurityError):
        safe_join(root, "../etc/passwd")


def test_safe_join_rejects_deep_parent_escape(root):
    with pytest.raises(SecurityError):
        safe_join(root, "wp-content/../../escape")


def test_safe_join_rejects_absolute(root):
    with pytest.raises(SecurityError):
        safe_join(root, "/etc/passwd")


def test_safe_join_rejects_empty(root):
    with pytest.raises(SecurityError):
        safe_join(root, "")


def test_safe_join_rejects_special_chars(root):
    with pytest.raises(SecurityError):
        safe_join(root, "wp-content/theme;rm -rf.css")


def test_safe_join_normalizes_backslashes(root):
    result = safe_join(root, "wp-content\\themes\\x.css")
    assert "\\" not in result or os.name == "nt"