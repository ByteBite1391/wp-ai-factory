import os
from database import db
from models.models import Project, ProjectActivity
from services.project_service import (
    create_project, update_project, delete_project,
    duplicate_project, approve_architecture, stats,
)
from config import Config


def test_create_project_sets_status_and_workspace(ctx):
    p = create_project({"name": "Demo", "features": ["وبلاگ"], "pages": ["Homepage"]})
    assert p.status == "requirements"
    assert os.path.isdir(os.path.join(Config.WORKSPACE_DIR, p.slug))
    assert p.feature_list() == ["وبلاگ"]


def test_create_project_unique_slug(ctx):
    a = create_project({"name": "Same"})
    b = create_project({"name": "Same"})
    assert a.slug != b.slug
    assert b.slug.startswith("same")


def test_create_project_logs_activity(ctx):
    p = create_project({"name": "LogTest"})
    acts = ProjectActivity.query.filter_by(project_id=p.id).all()
    assert any("ایجاد" in a.action for a in acts)


def test_update_project_features(ctx, sample_project):
    update_project(sample_project, {
        "features": ["وبلاگ", "جست‌وجو"],
        "pages": ["Homepage"],
    })
    db.session.refresh(sample_project)
    assert sample_project.feature_list() == ["وبلاگ", "جست‌وجو"]
    assert sample_project.page_list() == ["Homepage"]


def test_delete_project_removes_workspace(ctx, sample_project):
    path = os.path.join(Config.WORKSPACE_DIR, sample_project.slug)
    assert os.path.isdir(path)
    delete_project(sample_project)
    assert not os.path.isdir(path)


def test_duplicate_project(ctx, sample_project):
    cp = duplicate_project(sample_project)
    assert cp.id != sample_project.id
    assert "کپی" in cp.name
    assert cp.feature_list() == sample_project.feature_list()


def test_approve_architecture_sets_flag(ctx, sample_project):
    approve_architecture(sample_project, {"website": ["A"], "features": ["B"]})
    db.session.refresh(sample_project)
    assert sample_project.architecture_approved is True
    assert sample_project.architecture.approved is True


def test_stats(ctx):
    create_project({"name": "A"})
    create_project({"name": "B"})
    s = stats()
    assert s["total"] >= 2
    assert "recent" in s and "activities" in s