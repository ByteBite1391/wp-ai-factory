import os
import sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


@pytest.fixture
def app(tmp_path, monkeypatch):
    """هر تست یک اپ Flask با DB و پوشه‌های مستقل می‌گیرد."""
    from config import Config

    instance = tmp_path / "instance"
    workspace = tmp_path / "workspace"
    exports = tmp_path / "exports"
    backups = tmp_path / "backups"
    for d in (instance, workspace, exports, backups):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Config, "INSTANCE_DIR", str(instance))
    monkeypatch.setattr(Config, "WORKSPACE_DIR", str(workspace))
    monkeypatch.setattr(Config, "EXPORTS_DIR", str(exports))
    monkeypatch.setattr(Config, "BACKUPS_DIR", str(backups))
    monkeypatch.setattr(
        Config,
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{instance}/test.db",
    )
    monkeypatch.setattr(Config, "SECRET_KEY", "test-secret")

    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


@pytest.fixture
def sample_project(ctx):
    """یک پروژه آماده برای تست‌های سرویس."""
    from services.project_service import create_project
    return create_project({
        "name": "فروشگاه دیجیتال",
        "project_type": "فروشگاهی",
        "customer_requirements": "فروشگاه لوازم دیجیتال با درگاه پرداخت",
        "website_language": "fa",
        "design_preferences": "مینیمال، طلایی",
        "wordpress_version": "6.5",
        "features": ["فروشگاه", "سبد خرید", "پرداخت"],
        "pages": ["Homepage", "Shop", "Contact"],
    })