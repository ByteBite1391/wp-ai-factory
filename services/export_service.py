import os
import zipfile
from datetime import datetime
from config import Config


def _zip_dir(src_dir, zip_path, arc_root=""):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, _, files in os.walk(src_dir):
            for file in files:
                full = os.path.join(folder, file)
                rel = os.path.relpath(full, src_dir)
                arc = os.path.join(arc_root, rel) if arc_root else rel
                z.write(full, arc)


def export_wp_content(project):
    root = os.path.join(Config.WORKSPACE_DIR, project.slug, "wp-content")
    if not os.path.isdir(root):
        raise FileNotFoundError("پوشه wp-content وجود ندارد.")
    out = os.path.join(Config.EXPORTS_DIR, f"{project.slug}-wp-content.zip")
    _zip_dir(root, out, arc_root="wp-content")
    return out


def export_theme(project):
    root = os.path.join(Config.WORKSPACE_DIR, project.slug, "wp-content", "themes")
    if not os.path.isdir(root):
        raise FileNotFoundError("پوشه themes وجود ندارد.")
    out = os.path.join(Config.EXPORTS_DIR, f"{project.slug}-theme.zip")
    _zip_dir(root, out)
    return out


def export_plugins(project):
    root = os.path.join(Config.WORKSPACE_DIR, project.slug, "wp-content", "plugins")
    if not os.path.isdir(root):
        raise FileNotFoundError("پوشه plugins وجود ندارد.")
    out = os.path.join(Config.EXPORTS_DIR, f"{project.slug}-plugins.zip")
    _zip_dir(root, out)
    return out


def export_report(project):
    root = os.path.join(Config.WORKSPACE_DIR, project.slug)
    if not os.path.isdir(root):
        raise FileNotFoundError("workspace خالی است.")
    out = os.path.join(Config.EXPORTS_DIR, f"{project.slug}-report.html")

    rows = []
    for folder, _, files in os.walk(root):
        for f in files:
            full = os.path.join(folder, f)
            rel = os.path.relpath(full, root).replace("\\", "/")
            rows.append(f"<tr><td>{rel}</td><td>{os.path.getsize(full)}</td></tr>")

    html = f"""<!doctype html><html dir="rtl" lang="fa"><meta charset="utf-8">
<title>گزارش {project.name}</title>
<style>body{{font-family:sans-serif;background:#09090B;color:#F5F5F5;padding:24px}}
table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #333;padding:6px}}
th{{background:#141418;color:#D4AF37}}</style>
<h1>گزارش پروژه {project.name}</h1>
<p>تاریخ: {datetime.utcnow().isoformat()}</p>
<table><tr><th>مسیر</th><th>اندازه (بایت)</th></tr>{''.join(rows)}</table>
</html>"""
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out