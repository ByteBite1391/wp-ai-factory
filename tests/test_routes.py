from database import db
from models.models import Project


# ---------- Dashboard ----------
def test_dashboard_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "داشبورد" in r.get_data(as_text=True)


# ---------- Projects ----------
def test_projects_list_ok(client):
    r = client.get("/projects/")
    assert r.status_code == 200


def test_create_project_form_get(client):
    r = client.get("/projects/create")
    assert r.status_code == 200
    assert "پروژه جدید" in r.get_data(as_text=True)


def test_create_project_post(client, app):
    r = client.post("/projects/create", data={
        "name": "Route Test",
        "project_type": "شرکتی",
        "customer_requirements": "توضیح",
        "website_language": "fa",
        "wordpress_version": "6.5",
        "features": ["وبلاگ"],
        "pages": "Homepage\nContact",
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Project.query.filter_by(name="Route Test").count() == 1


def test_create_project_missing_name_flashes(client):
    r = client.post("/projects/create", data={"name": ""}, follow_redirects=True)
    assert r.status_code == 200
    assert "الزامی" in r.get_data(as_text=True)


def test_project_detail_ok(client, app, sample_project):
    r = client.get(f"/projects/{sample_project.id}")
    assert r.status_code == 200
    assert sample_project.name in r.get_data(as_text=True)


def test_project_detail_404(client):
    r = client.get("/projects/99999")
    assert r.status_code == 404


def test_project_edit_get(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/edit")
    assert r.status_code == 200


def test_project_edit_post(client, app, sample_project):
    r = client.post(f"/projects/{sample_project.id}/edit", data={
        "name": "Edited",
        "project_type": "شخصی",
        "customer_requirements": "",
        "website_language": "fa",
        "wordpress_version": "6.5",
        "features": ["جست‌وجو"],
        "pages": "Homepage",
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        p = Project.query.get(sample_project.id)
        assert p.name == "Edited"
        assert p.feature_list() == ["جست‌وجو"]


def test_project_delete(client, app, sample_project):
    pid = sample_project.id
    r = client.post(f"/projects/{pid}/delete", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Project.query.get(pid) is None


def test_project_duplicate(client, app, sample_project):
    r = client.post(f"/projects/{sample_project.id}/duplicate",
                    follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Project.query.filter(Project.name.contains("کپی")).count() >= 1


def test_architecture_get(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/architecture")
    assert r.status_code == 200


def test_architecture_post(client, app, sample_project):
    r = client.post(f"/projects/{sample_project.id}/architecture", data={
        "pages": "Homepage\nAbout",
        "features": "فروشگاه",
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        p = Project.query.get(sample_project.id)
        assert p.architecture_approved is True


# ---------- Prompts ----------
def test_prompts_page_get(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/prompts/")
    assert r.status_code == 200


def test_prompts_generate(client, app, sample_project):
    r = client.post(f"/projects/{sample_project.id}/prompts/",
                    data={"stage": "requirements_analysis"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert "تولید" in r.get_data(as_text=True)


def test_prompts_blocked_without_approval(client, app, sample_project):
    r = client.post(f"/projects/{sample_project.id}/prompts/",
                    data={"stage": "theme_generation"},
                    follow_redirects=True)
    body = r.get_data(as_text=True)
    assert "تأیید" in body or "معماری" in body


# ---------- Imports ----------
def test_imports_page_get(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/imports/")
    assert r.status_code == 200


def test_imports_valid_json(client, app, sample_project):
    import json
    payload = json.dumps({
        "project_id": sample_project.slug,
        "batch_id": "b1",
        "files": [{
            "path": "wp-content/themes/t/style.css",
            "content": "/*x*/",
        }],
        "completed": True,
    })
    r = client.post(f"/projects/{sample_project.id}/imports/",
                    data={"raw": payload}, follow_redirects=True)
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "Import" in body or "نوشته" in body


def test_imports_invalid_json(client, sample_project):
    r = client.post(f"/projects/{sample_project.id}/imports/",
                    data={"raw": "totally not json"}, follow_redirects=True)
    assert r.status_code == 200


def test_imports_path_escape_rejected(client, app, sample_project):
    import json
    payload = json.dumps({
        "project_id": sample_project.slug,
        "files": [{"path": "../etc/passwd", "content": "x"}],
        "completed": True,
    })
    r = client.post(f"/projects/{sample_project.id}/imports/",
                    data={"raw": payload}, follow_redirects=True)
    assert r.status_code == 200


# ---------- Files ----------
def test_files_page_get(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/files/")
    assert r.status_code == 200


def test_files_view(client, app, sample_project):
    from services import file_service
    with app.app_context():
        file_service.write_files(sample_project, [
            {"path": "wp-content/x.txt", "content": "hello"},
        ])
    r = client.get(f"/projects/{sample_project.id}/files/?path=wp-content/x.txt")
    assert r.status_code == 200
    assert "hello" in r.get_data(as_text=True)


def test_files_save(client, app, sample_project):
    from services import file_service
    with app.app_context():
        file_service.write_files(sample_project, [
            {"path": "wp-content/y.txt", "content": "old"},
        ])
    r = client.post(f"/projects/{sample_project.id}/files/save", data={
        "path": "wp-content/y.txt",
        "content": "new",
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert file_service.read_file(sample_project, "wp-content/y.txt") == "new"


def test_files_backup(client, app, sample_project):
    from services import file_service, backup_service
    with app.app_context():
        file_service.write_files(sample_project, [
            {"path": "wp-content/z.txt", "content": "x"},
        ])
    r = client.post(f"/projects/{sample_project.id}/files/backup",
                    follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert len(backup_service.list_backups(sample_project)) >= 1


# ---------- Exports ----------
def test_exports_page_get(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/exports/")
    assert r.status_code == 200


def test_exports_wp_content(client, app, sample_project):
    from services import file_service
    with app.app_context():
        file_service.write_files(sample_project, [
            {"path": "wp-content/themes/t/style.css", "content": "/*x*/"},
        ])
    r = client.get(f"/projects/{sample_project.id}/exports/wp-content")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/zip") or \
           "attachment" in r.headers.get("Content-Disposition", "")


def test_exports_invalid_kind_redirects(client, sample_project):
    r = client.get(f"/projects/{sample_project.id}/exports/unknown",
                   follow_redirects=True)
    assert r.status_code == 200


# ---------- Help ----------
def test_help_index(client):
    r = client.get("/help/")
    assert r.status_code == 200
    assert "راهنما" in r.get_data(as_text=True)


def test_help_article(client):
    # seed_help در create_app اجرا می‌شود
    r = client.get("/help/intro")
    assert r.status_code == 200


def test_help_search(client):
    r = client.get("/help/?q=JSON")
    assert r.status_code == 200
    assert "JSON" in r.get_data(as_text=True)


def test_help_unknown_article_404(client):
    r = client.get("/help/does-not-exist")
    assert r.status_code == 404


# ---------- Security E2E ----------
def test_imports_cannot_escape_workspace(client, app, sample_project):
    import json, os
    from config import Config
    payload = json.dumps({
        "project_id": sample_project.slug,
        "files": [{"path": "../escape.txt", "content": "x"}],
        "completed": True,
    })
    client.post(f"/projects/{sample_project.id}/imports/",
                data={"raw": payload}, follow_redirects=True)
    outside = os.path.join(Config.WORKSPACE_DIR, "..", "escape.txt")
    assert not os.path.exists(outside)