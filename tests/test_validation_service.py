import pytest
from services.validation_service import check_php_syntax, validate_files
from services import file_service


def test_check_php_no_php():
    ok, msg = check_php_syntax("just text")
    assert ok is True
    assert "بدون" in msg or "no" in msg.lower()


def test_check_php_balanced_fallback(monkeypatch):
    import services.validation_service as v
    monkeypatch.setattr(v.shutil, "which", lambda _: None)
    ok, msg = check_php_syntax("<?php function x() { return 1; }")
    assert ok is True


def test_check_php_unbalanced_fallback(monkeypatch):
    import services.validation_service as v
    monkeypatch.setattr(v.shutil, "which", lambda _: None)
    ok, msg = check_php_syntax("<?php function x() { return 1;")
    assert ok is False


def test_validate_files_ok(ctx, sample_project):
    files = [{"path": "wp-content/a.css", "content": "/*x*/"}]
    result = validate_files(sample_project, files, sample_project.slug)
    assert result["errors"] == []
    assert len(result["valid_files"]) == 1


def test_validate_files_detects_bad_php(monkeypatch, ctx, sample_project):
    import services.validation_service as v
    monkeypatch.setattr(v.shutil, "which", lambda _: None)
    files = [{"path": "wp-content/b.php", "content": "<?php function x() {"}]
    result = validate_files(sample_project, files, sample_project.slug)
    assert result["warnings"]