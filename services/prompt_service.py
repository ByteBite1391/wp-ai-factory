import json
from database import db
from models.models import PromptHistory
from prompts.stages import STAGES, STAGE_TITLES, build_stage_prompt
from services.project_service import log


CODE_STAGES = {"theme_generation", "plugin_generation", "feature_implementation"}


def project_context(p):
    arch = p.architecture
    arch_text = ""
    if arch and arch.content:
        try:
            arch_text = json.dumps(json.loads(arch.content), ensure_ascii=False, indent=2)
        except Exception:
            arch_text = arch.content
    return {
        "name": p.name, "slug": p.slug, "type": p.project_type,
        "language": p.website_language, "wp_version": p.wordpress_version,
        "features": p.feature_list(), "pages": p.page_list(),
        "design": p.design_preferences, "requirements": p.customer_requirements,
        "architecture": arch_text,
    }


def generate_prompt(p, stage):
    if stage not in STAGE_TITLES:
        raise ValueError("مرحله نامعتبر است.")
    if stage in CODE_STAGES and not p.architecture_approved:
        raise ValueError("ابتدا باید معماری سایت تأیید شود.")
    text = build_stage_prompt(stage, project_context(p))
    db.session.add(PromptHistory(project_id=p.id, stage=stage, prompt_text=text))
    db.session.commit()
    log(p.id, "تولید پرامپت", STAGE_TITLES.get(stage, stage))
    return text


def history(p):
    return PromptHistory.query.filter_by(project_id=p.id)\
        .order_by(PromptHistory.created_at.desc()).all()


__all__ = ["generate_prompt", "history", "STAGES", "STAGE_TITLES"]