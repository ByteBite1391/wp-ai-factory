import os
from flask import Flask, render_template
from config import Config
from database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    for d in (Config.INSTANCE_DIR, Config.WORKSPACE_DIR,
              Config.EXPORTS_DIR, Config.BACKUPS_DIR):
        os.makedirs(d, exist_ok=True)

    db.init_app(app)

    from routes.dashboard import dashboard_bp
    from routes.projects import projects_bp
    from routes.prompts import prompts_bp
    from routes.imports import imports_bp
    from routes.files import files_bp
    from routes.exports import exports_bp
    from routes.help import help_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(prompts_bp, url_prefix="/projects/<int:project_id>/prompts")
    app.register_blueprint(imports_bp, url_prefix="/projects/<int:project_id>/imports")
    app.register_blueprint(files_bp,   url_prefix="/projects/<int:project_id>/files")
    app.register_blueprint(exports_bp, url_prefix="/projects/<int:project_id>/exports")
    app.register_blueprint(help_bp, url_prefix="/help")

    with app.app_context():
        db.create_all()
        from core.seed import seed_help
        seed_help()

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="صفحه یافت نشد"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="خطای سرور"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)