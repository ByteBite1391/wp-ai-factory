from database import db
from models.models import Project, ProjectRequirement, ProjectArchitecture


def test_create_project_via_orm(ctx):
    p = Project(name="T", slug="t")
    db.session.add(p)
    db.session.commit()
    assert p.id is not None


def test_feature_and_page_lists(ctx, sample_project):
    assert "فروشگاه" in sample_project.feature_list()
    assert "Homepage" in sample_project.page_list()
    assert "Webshop" not in sample_project.feature_list()


def test_requirement_kind_separation(ctx, sample_project):
    features = [r for r in sample_project.requirements if r.kind == "feature"]
    pages = [r for r in sample_project.requirements if r.kind == "page"]
    assert len(features) == 3
    assert len(pages) == 3


def test_architecture_relationship(ctx, sample_project):
    arch = sample_project.architecture
    assert arch is not None
    data = arch.data()
    assert "Homepage" in data["website"]
    assert "فروشگاه" in data["features"]


def test_cascade_delete(ctx, sample_project):
    pid = sample_project.id
    db.session.delete(sample_project)
    db.session.commit()
    assert Project.query.get(pid) is None
    assert ProjectRequirement.query.filter_by(project_id=pid).count() == 0
    assert ProjectArchitecture.query.filter_by(project_id=pid).count() == 0