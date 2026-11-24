from datetime import datetime
import json
from database import db


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    project_type = db.Column(db.String(100), default="company")
    customer_requirements = db.Column(db.Text, default="")
    website_language = db.Column(db.String(50), default="fa")
    design_preferences = db.Column(db.Text, default="")
    wordpress_version = db.Column(db.String(20), default="6.5")
    status = db.Column(db.String(50), default="draft", index=True)
    architecture_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirements = db.relationship("ProjectRequirement", backref="project",
                                   cascade="all, delete-orphan")
    architecture = db.relationship("ProjectArchitecture", backref="project",
                                   uselist=False, cascade="all, delete-orphan")
    files = db.relationship("ProjectFile", backref="project", cascade="all, delete-orphan")
    versions = db.relationship("ProjectVersion", backref="project", cascade="all, delete-orphan")
    prompts = db.relationship("PromptHistory", backref="project", cascade="all, delete-orphan")
    imports = db.relationship("ImportHistory", backref="project", cascade="all, delete-orphan")
    activities = db.relationship("ProjectActivity", backref="project",
                                 cascade="all, delete-orphan",
                                 order_by="ProjectActivity.created_at.desc()")

    def feature_list(self):
        return [r.name for r in self.requirements if r.kind == "feature"]

    def page_list(self):
        return [r.name for r in self.requirements if r.kind == "page"]


class ProjectRequirement(db.Model):
    __tablename__ = "project_requirements"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    kind = db.Column(db.String(20), default="feature")  # feature | page
    name = db.Column(db.String(150), nullable=False)


class ProjectArchitecture(db.Model):
    __tablename__ = "project_architecture"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, unique=True)
    content = db.Column(db.Text, default="{}")  # JSON
    approved = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def data(self):
        try:
            return json.loads(self.content or "{}")
        except Exception:
            return {}


class ProjectFile(db.Model):
    __tablename__ = "project_files"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    size = db.Column(db.Integer, default=0)
    checksum = db.Column(db.String(64), default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectVersion(db.Model):
    __tablename__ = "project_versions"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, default="")
    version_num = db.Column(db.Integer, default=1)
    note = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PromptHistory(db.Model):
    __tablename__ = "prompt_history"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    stage = db.Column(db.String(80), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ImportHistory(db.Model):
    __tablename__ = "import_history"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    batch_id = db.Column(db.String(80), default="")
    raw_response = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="pending")  # ok | partial | error
    files_count = db.Column(db.Integer, default=0)
    message = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProjectActivity(db.Model):
    __tablename__ = "project_activity"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    action = db.Column(db.String(120), nullable=False)
    detail = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class HelpCategory(db.Model):
    __tablename__ = "help_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    order = db.Column(db.Integer, default=0)
    articles = db.relationship("HelpArticle", backref="category",
                               cascade="all, delete-orphan")


class HelpArticle(db.Model):
    __tablename__ = "help_articles"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("help_categories.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, default="")
    order = db.Column(db.Integer, default=0)