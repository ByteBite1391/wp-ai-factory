import json
import re


class ParseError(Exception):
    pass


def extract_json(text: str) -> dict:
    if not text or not text.strip():
        raise ParseError("پاسخ خالی است.")

    # 1) try direct parse
    candidates = []

    # 2) fenced code blocks
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        candidates.append(m.group(1))

    # 3) first {...last}
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidates.append(text[first:last + 1])

    candidates.append(text.strip())

    for c in candidates:
        try:
            data = json.loads(c)
            if isinstance(data, dict):
                return data
        except Exception:
            continue
    raise ParseError("JSON معتبر پیدا نشد. مطمئن شوید پاسخ داخل ```json است.")


def validate_payload(data: dict, project_id: str):
    errors = []

    if not isinstance(data, dict):
        raise ParseError("ساختار پاسخ باید آبجکت JSON باشد.")

    pid = data.get("project_id")
    if pid and pid != project_id:
        errors.append(f"project_id در پاسخ ({pid}) با پروژه ({project_id}) هم‌خوانی ندارد.")

    files = data.get("files")
    if not isinstance(files, list):
        raise ParseError("فیلد files باید لیست باشد.")

    valid_files = []
    seen = set()
    for i, f in enumerate(files):
        if not isinstance(f, dict):
            errors.append(f"فایل شماره {i} آبجکت نیست.")
            continue
        path = (f.get("path") or "").replace("\\", "/").strip()
        content = f.get("content", "")
        if not path:
            errors.append(f"فایل شماره {i} فاقد path است.")
            continue
        if path.startswith("/") or ".." in path.split("/"):
            errors.append(f"مسیر نامعتبر: {path}")
            continue
        if not (path.startswith("wp-content/") or path.startswith("docs/")):
            errors.append(f"مسیر خارج از محدوده مجاز: {path}")
            continue
        if path in seen:
            errors.append(f"فایل تکراری: {path}")
            continue
        seen.add(path)
        valid_files.append({"path": path, "content": content})

    return {
        "valid_files": valid_files,
        "errors": errors,
        "completed": bool(data.get("completed", True)),
        "batch_id": data.get("batch_id", ""),
        "message": data.get("message", ""),
    }