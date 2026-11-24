from flask import Blueprint, render_template, request, abort
from models.models import HelpCategory, HelpArticle

help_bp = Blueprint("help", __name__)


@help_bp.route("/")
def index():
    cats = HelpCategory.query.order_by(HelpCategory.order).all()
    q = request.args.get("q", "").strip()
    if q:
        results = HelpArticle.query.filter(HelpArticle.title.contains(q)).all()
    else:
        results = []
    return render_template("help/index.html", cats=cats, q=q, results=results)


@help_bp.route("/<slug>")
def article(slug):
    art = HelpArticle.query.filter_by(slug=slug).first_or_404()
    cats = HelpCategory.query.order_by(HelpCategory.order).all()
    return render_template("help/article.html", art=art, cats=cats)