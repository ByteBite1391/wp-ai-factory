import os
import json
from datetime import datetime
from database import db
from models.models import ProjectFile, ProjectVersion
from core.security import safe_join, SecurityError
from core.helpers import checksum
from config import Config
from services.project_service import log


def project_root(project):
    root = os.path.join(Config.WORKSPACE_DIR, project.slug)
    os.makedirs(root, exist_ok=True)
    return root


def write_files(project, files, note=""):
    root = project_root(project)
    results = {"written": [], "errors": []}

    for f in files:
        try:
            full = safe_join(root, f["path"])
        except SecurityError as e:
            results["errors"].append(str(e))
            continue

        os.makedirs(os.path.dirname(full), exist_ok=True)

        # backup previous content as version
        if os.path.isfile(full):
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as fp:
                    old = fp.read()
                last = ProjectVersion.query.filter_by(project_id=project.id,
                                                      path=f["path"])\
                    .order_by(ProjectVersion.version_num.desc()).first()
                vnum = (last.version_num + 1) if last else 1
                db.session.add(ProjectVersion(project_id=project.id, path=f["path"],
                                              content=old, version_num=vnum,
                                              note=note or "نسخه قبلی"))
            except Exception:
                pass

        with open(full, "w", encoding="utf-8") as fp:
            fp.write(f["content"])

        meta = ProjectFile.query.filter_by(project_id=project.id, path=f["path"]).first()
        if not meta:
            meta = ProjectFile(project_id=project.id, path=f["path"])
            db.session.add(meta)
        meta.size = len(f["content"].encode("utf-8"))
        meta.checksum = checksum(f["content"])
        results["written"].append(f["path"])

    db.session.commit()
    log(project.id, "نوشتن فایل‌ها", f"{len(results['written'])} فایل")
    return results


def build_tree(project):
    root = project_root(project)
    tree = {"name": "/", "type": "dir", "children": []}

    def walk(node, path):
        try:
            entries = sorted(os.listdir(path))
        except FileNotFoundError:
            return
        for entry in entries:
            full = os.path.join(path, entry)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if os.path.isdir(full):
                child = {"name": entry, "type": "dir", "rel": rel, "children": []}
                node["children"].append(child)
                walk(child, full)
            else:
                node["children"].append({"name": entry, "type": "file", "rel": rel})

    walk(tree, root)
    return tree


def read_file(project, rel_path):
    root = project_root(project)
    full = safe_join(root, rel_path)
    if not os.path.isfile(full):
        raise FileNotFoundError(rel_path)
    with open(full, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def save_file(project, rel_path, content):
    root = project_root(project)
    full = safe_join(root, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if os.path.isfile(full):
        with open(full, "r", encoding="utf-8", errors="ignore") as fp:
            old = fp.read()
        last = ProjectVersion.query.filter_by(project_id=project.id, path=rel_path)\
            .order_by(ProjectVersion.version_num.desc()).first()
        vnum = (last.version_num + 1) if last else 1
        db.session.add(ProjectVersion(project_id=project.id, path=rel_path,
                                      content=old, version_num=vnum,
                                      note="ویرایش دستی"))
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    db.session.commit()
    log(project.id, "ویرایش فایل", rel_path)


def delete_file(project, rel_path):
    root = project_root(project)
    full = safe_join(root, rel_path)
    if os.path.isfile(full):
        os.remove(full)
        ProjectFile.query.filter_by(project_id=project.id, path=rel_path).delete()
        db.session.commit()
        log(project.id, "حذف فایل", rel_path)
        return True
    return False


def file_history(project, rel_path):
    return ProjectVersion.query.filter_by(project_id=project.id, path=rel_path)\
        .order_by(ProjectVersion.version_num.desc()).all()