from flask import Blueprint, render_template, send_file, flash, redirect, url_for
from models.models import Project
from services import export_service
import os

exports_bp = Blueprint("exports", __name__)


@exports_bp.route("/")
def index(project_id):
    p = Project.query.get_or_404(project_id)
    return render_template("exports/index.html", p=p)


@exports_bp.route("/<kind>")
def download(project_id, kind):
    p = Project.query.get_or_404(project_id)
    fns = {
        "wp-content": export_service.export_wp_content,
        "theme": export_service.export_theme,
        "plugins": export_service.export_plugins,
        "report": export_service.export_report,
    }
    if kind not in fns:
        flash("نوع خروجی نامعتبر است.", "error")
        return redirect(url_for("exports.index", project_id=p.id))
    try:
        path = fns[kind](p)
        return send_file(path, as_attachment=True)
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for("exports.index", project_id=p.id))