import os
import re

SAFE_PATH = re.compile(r"^[A-Za-z0-9_\-\/\.]+$")


class SecurityError(Exception):
    pass


def safe_join(root: str, rel_path: str) -> str:
    if not rel_path:
        raise SecurityError("مسیر خالی است.")
    rel_path = rel_path.replace("\\", "/").strip()
    if rel_path.startswith("/") or ".." in rel_path.split("/"):
        raise SecurityError(f"مسیر نامعتبر: {rel_path}")
    if not SAFE_PATH.match(rel_path):
        raise SecurityError(f"کاراکترهای غیرمجاز در مسیر: {rel_path}")
    root = os.path.abspath(root)
    full = os.path.abspath(os.path.join(root, rel_path))
    if not (full == root or full.startswith(root + os.sep)):
        raise SecurityError(f"خروج از workspace: {rel_path}")
    return full