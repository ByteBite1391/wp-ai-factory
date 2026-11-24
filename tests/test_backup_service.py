import os
import pytest
from services import file_service, backup_service
from config import Config


def test_backup_project(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/a.txt", "content": "x"},
    ])
    dest = backup_service.backup_project(sample_project)
    assert os.path.isdir(dest)
    assert os.path.isfile(os.path.join(dest, "wp-content", "a.txt"))


def test_list_backups(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/a.txt", "content": "x"},
    ])
    backup_service.backup_project(sample_project)
    ls = backup_service.list_backups(sample_project)
    assert len(ls) >= 1


def test_restore_backup(ctx, sample_project):
    file_service.write_files(sample_project, [
        {"path": "wp-content/a.txt", "content": "original"},
    ])
    backup_service.backup_project(sample_project)
    backup_name = backup_service.list_backups(sample_project)[0]

    file_service.write_files(sample_project, [
        {"path": "wp-content/a.txt", "content": "modified"},
    ])

    backup_service.restore_backup(sample_project, backup_name)
    content = file_service.read_file(sample_project, "wp-content/a.txt")
    assert content == "original"


def test_restore_missing_raises(ctx, sample_project):
    with pytest.raises(FileNotFoundError):
        backup_service.restore_backup(sample_project, "does-not-exist")