from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from models.models import Project
from services import file_service
from services.backup_service import backup_project, list_backups, restore_backup
from core.security import SecurityError

files_bp = Blueprint("files", __name__)


@files_bp.route("/")
def index(project_id):
    p = Project.query.get_or_404(project_id)
    tree = file_service.build_tree(p)
    current = request.args.get("path")
    content = None
    if current:
        try:
            content = file_service.read_file(p, current)
        except (FileNotFoundError, SecurityError):
            flash("فایل یافت نشد یا مسیر نامعتبر است.", "error")
            current = None
    return render_template("files/index.html", p=p, tree=tree,
                           current=current, content=content,
                           backups=list_backups(p))


@files_bp.route("/save", methods=["POST"])
def save(project_id):
    p = Project.query.get_or_404(project_id)
    path = request.form.get("path")
    content = request.form.get("content", "")
    try:
        file_service.save_file(p, path, content)
        flash("فایل ذخیره شد.", "success")
    except SecurityError as e:
        flash(str(e), "error")
    return redirect(url_for("files.index", project_id=p.id, path=path))


@files_bp.route("/delete", methods=["POST"])
def delete(project_id):
    p = Project.query.get_or_404(project_id)
    path = request.form.get("path")
    try:
        file_service.delete_file(p, path)
        flash("فایل حذف شد.", "success")
    except SecurityError as e:
        flash(str(e), "error")
    return redirect(url_for("files.index", project_id=p.id))


@files_bp.route("/backup", methods=["POST"])
def backup(project_id):
    p = Project.query.get_or_404(project_id)
    try:
        backup_project(p)
        flash("نسخه پشتیبان ساخته شد.", "success")
    except FileNotFoundError as e:
        flash(str(e), "error")
    return redirect(url_for("files.index", project_id=p.id))


@files_bp.route("/restore", methods=["POST"])
def restore(project_id):
    p = Project.query.get_or_404(project_id)
    name = request.form.get("name")
    try:
        restore_backup(p, name)
        flash("بازیابی انجام شد.", "success")
    except FileNotFoundError:
        flash("نسخه پشتیبان یافت نشد.", "error")
    return redirect(url_for("files.index", project_id=p.id))