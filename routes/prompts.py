from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.models import Project
from services.prompt_service import generate_prompt, history, STAGES

prompts_bp = Blueprint("prompts", __name__)


@prompts_bp.route("/", methods=["GET", "POST"])
def index(project_id):
    p = Project.query.get_or_404(project_id)
    prompt_text = None
    selected = request.form.get("stage") if request.method == "POST" else None

    if request.method == "POST":
        stage = request.form.get("stage")
        if not stage:
            flash("مرحله را انتخاب کنید.", "error")
        else:
            try:
                prompt_text = generate_prompt(p, stage)
                flash("پرامپت تولید شد.", "success")
            except ValueError as e:
                flash(str(e), "error")

    return render_template("prompts/index.html", p=p, stages=STAGES,
                           prompt_text=prompt_text, selected=selected,
                           history=history(p))