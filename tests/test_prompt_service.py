import pytest
from database import db
from models.models import PromptHistory
from services.project_service import create_project, approve_architecture
from services.prompt_service import generate_prompt, history, CODE_STAGES


def test_code_stage_requires_approved_architecture(ctx, sample_project):
    with pytest.raises(ValueError):
        generate_prompt(sample_project, "theme_generation")


def test_analysis_stage_no_approval_needed(ctx, sample_project):
    text = generate_prompt(sample_project, "requirements_analysis")
    assert "نیازمندی" in text
    assert sample_project.name in text


def test_code_stage_works_after_approval(ctx, sample_project):
    approve_architecture(sample_project, {"website": ["Home"], "features": ["Shop"]})
    db.session.refresh(sample_project)
    text = generate_prompt(sample_project, "theme_generation")
    assert "wp-content/themes/custom-theme" in text
    assert "json" in text.lower()


def test_prompt_contains_project_data(ctx, sample_project):
    text = generate_prompt(sample_project, "architecture_design")
    assert "فروشگاهی" in text
    assert "سبد خرید" in text
    assert "6.5" in text


def test_history_records(ctx, sample_project):
    generate_prompt(sample_project, "requirements_analysis")
    generate_prompt(sample_project, "architecture_design")
    records = history(sample_project)
    assert len(records) == 2
    assert {r.stage for r in records} == {"requirements_analysis", "architecture_design"}


def test_invalid_stage(ctx, sample_project):
    with pytest.raises(ValueError):
        generate_prompt(sample_project, "nonexistent_stage")


def test_all_code_stages_require_approval(ctx, sample_project):
    for st in CODE_STAGES:
        with pytest.raises(ValueError):
            generate_prompt(sample_project, st)