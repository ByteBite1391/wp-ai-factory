import os
import pytest
import zipfile
from services import file_service, export_service
from config import Config


def _prepare(ctx, p):
    file_service.write_files(p, [
        {"path": "wp-content/themes/t/style.css", "content": "/*t*/"},
        {"path": "wp-content/plugins/x/x.php", "content": "<?php echo 1;"},
        {"path": "docs/r.md", "content": "# R"},
    ])


def test_export_wp_content(ctx, sample_project):
    _prepare(ctx, sample_project)
    path = export_service.export_wp_content(sample_project)
    assert os.path.isfile(path)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    assert any(n.startswith("wp-content/") for n in names)


def test_export_theme(ctx, sample_project):
    _prepare(ctx, sample_project)
    path = export_service.export_theme(sample_project)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    assert any("style.css" in n for n in names)


def test_export_plugins(ctx, sample_project):
    _prepare(ctx, sample_project)
    path = export_service.export_plugins(sample_project)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    assert any(n.endswith("x.php") for n in names)


def test_export_report(ctx, sample_project):
    _prepare(ctx, sample_project)
    path = export_service.export_report(sample_project)
    with open(path, encoding="utf-8") as f:
        html = f.read()
    assert sample_project.name in html
    assert "wp-content/themes/t/style.css" in html


def test_export_missing_dir_raises(ctx, sample_project):
    with pytest.raises(FileNotFoundError):
        export_service.export_theme(sample_project)