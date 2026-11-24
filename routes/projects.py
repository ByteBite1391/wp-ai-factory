from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db
from models.models import Project, ProjectActivity
from services.project_service import (create_project, update_project, delete_project,
                                      duplicate_project, approve_architecture, log)
from prompts.stages import STAGES

projects_bp = Blueprint("projects", __name__)

TYPES = ["فروشگاهی", "شرکتی", "شخصی", "خبری", "آموزشی",
         "وبلاگی", "خدماتی", "نمونه‌کار", "اختصاصی"]

ALL_FEATURES = ["فروشگاه", "محصولات", "سبد خرید", "پرداخت", "وبلاگ",
                "حساب کاربری", "ثبت‌نام", "ورود", "پنل مدیریت",
                "سیستم رزرو", "سیستم نوبت‌دهی", "فرم تماس",
                "جست‌وجو", "فیلتر", "چندزبانه", "سیستم عضویت"]


@projects_bp.route("/")
def list_projects():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    query = Project.query
    if q:
        query = query.filter(Project.name.contains(q))
    if status:
        query = query.filter_by(status=status)
    projects = query.order_by(Project.updated_at.desc()).all()
    return render_template("projects/list.html", projects=projects,
                           q=q, status=status, types=TYPES)


@projects_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "project_type": request.form.get("project_type", "شرکتی"),
            "customer_requirements": request.form.get("customer_requirements", ""),
            "website_language": request.form.get("website_language", "fa"),
            "design_preferences": request.form.get("design_preferences", ""),
            "wordpress_version": request.form.get("wordpress_version", "6.5"),
            "features": request.form.getlist("features"),
            "pages": [p.strip() for p in
                      request.form.get("pages", "").splitlines() if p.strip()],
        }
        if not data["name"]:
            flash("نام پروژه الزامی است.", "error")
            return redirect(url_for("projects.create"))
        p = create_project(data)
        flash("پروژه ساخته شد.", "success")
        return redirect(url_for("projects.detail", project_id=p.id))
    return render_template("projects/form.html", project=None, types=TYPES,
                           all_features=ALL_FEATURES)


@projects_bp.route("/<int:project_id>")
def detail(project_id):
    p = Project.query.get_or_404(project_id)
    return render_template("projects/detail.html", p=p, stages=STAGES,
                           activities=p.activities[:10])


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
def edit(project_id):
    p = Project.query.get_or_404(project_id)
    if request.method == "POST":
        data = {
            "name": request.form.get("name", p.name).strip(),
            "project_type": request.form.get("project_type", p.project_type),
            "customer_requirements": request.form.get("customer_requirements", ""),
            "website_language": request.form.get("website_language", "fa"),
            "design_preferences": request.form.get("design_preferences", ""),
            "wordpress_version": request.form.get("wordpress_version", "6.5"),
            "features": request.form.getlist("features"),
            "pages": [x.strip() for x in
                      request.form.get("pages", "").splitlines() if x.strip()],
        }
        update_project(p, data)
        flash("پروژه ویرایش شد.", "success")
        return redirect(url_for("projects.detail", project_id=p.id))
    return render_template("projects/form.html", project=p, types=TYPES,
                           all_features=ALL_FEATURES)


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
def delete(project_id):
    p = Project.query.get_or_404(project_id)
    delete_project(p)
    flash("پروژه حذف شد.", "success")
    return redirect(url_for("projects.list_projects"))


@projects_bp.route("/<int:project_id>/duplicate", methods=["POST"])
def duplicate(project_id):
    p = Project.query.get_or_404(project_id)
    np = duplicate_project(p)
    flash("کپی پروژه ساخته شد.", "success")
    return redirect(url_for("projects.detail", project_id=np.id))


@projects_bp.route("/<int:project_id>/architecture", methods=["GET", "POST"])
def architecture(project_id):
    p = Project.query.get_or_404(project_id)
    if request.method == "POST":
        pages = [x.strip() for x in request.form.get("pages", "").splitlines() if x.strip()]
        features = [x.strip() for x in
                    request.form.get("features", "").splitlines() if x.strip()]
        approve_architecture(p, {"website": pages, "features": features})
        flash("معماری تأیید و ذخیره شد.", "success")
        return redirect(url_for("projects.detail", project_id=p.id))

    arch = p.architecture.data() if p.architecture else {}
    return render_template("projects/architecture.html", p=p, arch=arch)