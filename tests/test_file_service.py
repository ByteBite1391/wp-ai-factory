import os
import pytest
from database import db
from services import file_service
from config import Config
from core.security import SecurityError


def _root(p):
    return os.path.join(Config.WORKSPACE_DIR, p.slug)


def test_write_files_creates_content(ctx, sample_project):
    res = file_service.write_files(sample_project, [
        {"path": "wp-content/themes/t/style.css", "content": "/*A*/"},
        {"path": "docs/readme.md", "content": "# Hi"},
    ])
    assert len(res["written"]) == 2
    assert res["errors"] == []
    full = os.path.join(_root(sample_project), "wp-content/themes/t/style.css")
    with open(full, "r", encoding="utf-8") as f:
        assert f.read() == "/*A*/"


def test_write_files_rejects_escape(ctx, sample_project):
    res = file_service.write_files(sample_project, [
        {"path": "../etc/passwd", "content": "x"},
    ])
    assert res["errors"]
    assert res["written"] == []


def test_write_files_overwrites_and_creates_version(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/x.txt", "content": "v1"},
    ])
    file_service.write_files(sample_project, [
        {"path": "wp-content/x.txt", "content": "v2"},
    ])
    with open(os.path.join(_root(sample_project), "wp-content/x.txt"),
              encoding="utf-8") as f:
        assert f.read() == "v2"
    hist = file_service.file_history(sample_project, "wp-content/x.txt")
    assert len(hist) == 1
    assert hist[0].content == "v1"


def test_read_file_ok(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/r.txt", "content": "hello"},
    ])
    assert file_service.read_file(sample_project, "wp-content/r.txt") == "hello"


def test_read_file_missing(ctx, sample_project):
    with pytest.raises(FileNotFoundError):
        file_service.read_file(sample_project, "wp-content/none.txt")


def test_save_file_versioning(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/s.txt", "content": "old"},
    ])
    file_service.save_file(sample_project, "wp-content/s.txt", "new")
    hist = file_service.file_history(sample_project, "wp-content/s.txt")
    assert any(h.content == "old" for h in hist)


def test_delete_file(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/d.txt", "content": "x"},
    ])
    assert file_service.delete_file(sample_project, "wp-content/d.txt") is True
    with pytest.raises(FileNotFoundError):
        file_service.read_file(sample_project, "wp-content/d.txt")


def test_delete_missing_returns_false(ctx, sample_project):
    assert file_service.delete_file(sample_project, "wp-content/none.txt") is False


def test_build_tree(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/themes/a/style.css", "content": "x"},
        {"path": "wp-content/plugins/b/b.php", "content": "<?php echo 1;"},
        {"path": "docs/r.md", "content": "# R"},
    ])
    tree = file_service.build_tree(sample_project)
    assert tree["type"] == "dir"
    names = {c["name"] for c in tree["children"]}
    assert {"wp-content", "docs"} <= names