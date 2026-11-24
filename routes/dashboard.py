from flask import Blueprint, render_template
from services.project_service import stats

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("dashboard.html", s=stats())