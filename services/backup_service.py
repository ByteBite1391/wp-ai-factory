import os
import shutil
from datetime import datetime
from config import Config


def backup_project(project):
    src = os.path.join(Config.WORKSPACE_DIR, project.slug)
    if not os.path.isdir(src):
        raise FileNotFoundError("workspace وجود ندارد.")
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(Config.BACKUPS_DIR, project.slug, ts)
    os.makedirs(dest, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return dest


def list_backups(project):
    base = os.path.join(Config.BACKUPS_DIR, project.slug)
    if not os.path.isdir(base):
        return []
    return sorted(os.listdir(base), reverse=True)


def restore_backup(project, name):
    src = os.path.join(Config.BACKUPS_DIR, project.slug, name)
    dest = os.path.join(Config.WORKSPACE_DIR, project.slug)
    if not os.path.isdir(src):
        raise FileNotFoundError(name)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return True