import os
import shutil
import subprocess
import tempfile
from services.parser_service import validate_payload


def check_php_syntax(content: str):
    if "<?php" not in content:
        return True, "بدون PHP"
    php = shutil.which("php")
    if not php:
        # basic brace balance
        if content.count("{") != content.count("}"):
            return False, "عدم تعادل آکولاد در PHP"
        return True, "بررسی ساده (php نصب نیست)"
    with tempfile.NamedTemporaryFile("w", suffix=".php", delete=False,
                                     encoding="utf-8") as f:
        f.write(content)
        tmp = f.name
    try:
        r = subprocess.run([php, "-l", tmp], capture_output=True, text=True)
        return r.returncode == 0, r.stdout + r.stderr
    finally:
        os.unlink(tmp)


def validate_files(project, files, project_id):
    data = {"files": files}
    result = validate_payload(data, project_id)
    warnings = []
    for f in result["valid_files"]:
        ok, msg = check_php_syntax(f["content"])
        if not ok:
            warnings.append(f"{f['path']}: {msg}")
    result["warnings"] = warnings
    return result