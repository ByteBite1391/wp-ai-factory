import json
import os
import shutil
from database import db
from models.models import (Project, ProjectRequirement, ProjectArchitecture,
                           ProjectActivity)
from core.helpers import slugify
from config import Config


DEFAULT_FEATURES = ["فروشگاه", "وبلاگ", "فرم تماس", "حساب کاربری"]
DEFAULT_PAGES = ["Homepage", "About", "Contact"]


def log(project_id, action, detail=""):
    db.session.add(ProjectActivity(project_id=project_id, action=action, detail=detail))
    db.session.commit()


def create_project(data):
    slug = data.get("slug") or slugify(data["name"])
    base = slug
    i = 1
    while Project.query.filter_by(slug=slug).first():
        slug = f"{base}-{i}"
        i += 1

    p = Project(
        name=data["name"].strip(),
        slug=slug,
        project_type=data.get("project_type", "company"),
        customer_requirements=data.get("customer_requirements", ""),
        website_language=data.get("website_language", "fa"),
        design_preferences=data.get("design_preferences", ""),
        wordpress_version=data.get("wordpress_version", "6.5"),
        status="requirements",
    )
    db.session.add(p)
    db.session.flush()

    for feat in data.get("features") or DEFAULT_FEATURES:
        db.session.add(ProjectRequirement(project_id=p.id, kind="feature", name=feat))
    for page in data.get("pages") or DEFAULT_PAGES:
        db.session.add(ProjectRequirement(project_id=p.id, kind="page", name=page))

    arch = ProjectArchitecture(project_id=p.id, content=json.dumps({
        "website": [pg for pg in (data.get("pages") or DEFAULT_PAGES)],
        "features": data.get("features") or DEFAULT_FEATURES,
    }, ensure_ascii=False), approved=False)
    db.session.add(arch)

    os.makedirs(os.path.join(Config.WORKSPACE_DIR, slug), exist_ok=True)
    db.session.commit()
    log(p.id, "ایجاد پروژه", p.name)
    return p


def update_project(p, data):
    p.name = data.get("name", p.name)
    p.project_type = data.get("project_type", p.project_type)
    p.customer_requirements = data.get("customer_requirements", p.customer_requirements)
    p.website_language = data.get("website_language", p.website_language)
    p.design_preferences = data.get("design_preferences", p.design_preferences)
    p.wordpress_version = data.get("wordpress_version", p.wordpress_version)

    if "features" in data or "pages" in data:
        db.session.query(ProjectRequirement).filter_by(project_id=p.id).delete()
        for feat in data.get("features") or []:
            db.session.add(ProjectRequirement(project_id=p.id, kind="feature", name=feat))
        for page in data.get("pages") or []:
            db.session.add(ProjectRequirement(project_id=p.id, kind="page", name=page))

    db.session.commit()
    log(p.id, "ویرایش پروژه", p.name)
    return p


def delete_project(p):
    shutil.rmtree(os.path.join(Config.WORKSPACE_DIR, p.slug), ignore_errors=True)
    db.session.delete(p)
    db.session.commit()


def duplicate_project(p):
    data = {
        "name": p.name + " (کپی)",
        "project_type": p.project_type,
        "customer_requirements": p.customer_requirements,
        "website_language": p.website_language,
        "design_preferences": p.design_preferences,
        "wordpress_version": p.wordpress_version,
        "features": p.feature_list(),
        "pages": p.page_list(),
    }
    return create_project(data)


def approve_architecture(p, content):
    arch = p.architecture or ProjectArchitecture(project_id=p.id)
    arch.content = json.dumps(content, ensure_ascii=False)
    arch.approved = True
    p.architecture_approved = True
    p.status = "architecture"
    db.session.add(arch)
    db.session.commit()
    log(p.id, "تأیید معماری")
    return arch


def stats():
    total = Project.query.count()
    active = Project.query.filter(Project.status.in_(["requirements", "architecture", "generating"])).count()
    completed = Project.query.filter_by(status="completed").count()
    recent = Project.query.order_by(Project.updated_at.desc()).limit(5).all()
    activities = ProjectActivity.query.order_by(ProjectActivity.created_at.desc()).limit(10).all()
    return {"total": total, "active": active, "completed": completed,
            "recent": recent, "activities": activities}