from flask import Blueprint, render_template, request, flash, redirect, url_for
from database import db
from models.models import Project, ImportHistory
from services.parser_service import extract_json, validate_payload, ParseError
from services.file_service import write_files
from services.project_service import log

imports_bp = Blueprint("imports", __name__)


@imports_bp.route("/", methods=["GET", "POST"])
def index(project_id):
    p = Project.query.get_or_404(project_id)
    result = None

    if request.method == "POST":
        raw = request.form.get("raw", "").strip()
        if not raw:
            flash("پاسخ را وارد کنید.", "error")
        else:
            try:
                data = extract_json(raw)
                validated = validate_payload(data, p.slug)

                if validated["errors"]:
                    ih = ImportHistory(project_id=p.id,
                                       batch_id=validated["batch_id"],
                                       raw_response=raw,
                                       status="error",
                                       message="\n".join(validated["errors"]))
                    db.session.add(ih)
                    db.session.commit()
                    result = {"ok": False, "errors": validated["errors"],
                              "written": []}
                    flash("خطا در ساختار پاسخ.", "error")
                else:
                    wr = write_files(p, validated["valid_files"],
                                     note=f"Import {validated['batch_id']}")
                    status = "ok" if validated["completed"] else "partial"
                    if status == "ok" and p.status in ("requirements", "architecture", "generating"):
                        p.status = "generating"
                    if validated["completed"] and p.status == "generating":
                        p.status = "completed"
                    db.session.add(ImportHistory(
                        project_id=p.id, batch_id=validated["batch_id"],
                        raw_response=raw, status=status,
                        files_count=len(wr["written"]),
                        message=validated["message"]))
                    db.session.commit()
                    log(p.id, "Import پاسخ", f"{len(wr['written'])} فایل")
                    result = {"ok": True,
                              "written": wr["written"],
                              "errors": wr["errors"],
                              "partial": status == "partial"}
                    flash("پاسخ Import شد.", "success")
            except ParseError as e:
                flash(str(e), "error")
                result = {"ok": False, "errors": [str(e)], "written": []}

    return render_template("imports/index.html", p=p, result=result,
                           history=ImportHistory.query.filter_by(project_id=p.id)
                           .order_by(ImportHistory.created_at.desc()).all())