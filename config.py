import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "wp-ai-factory-change-this-secret")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "wpai.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
    EXPORTS_DIR   = os.path.join(BASE_DIR, "exports")
    BACKUPS_DIR   = os.path.join(BASE_DIR, "backups")
    INSTANCE_DIR  = os.path.join(BASE_DIR, "instance")