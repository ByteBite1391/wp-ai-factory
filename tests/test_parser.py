import pytest
from services.parser_service import extract_json, validate_payload, ParseError


VALID_JSON = '{"project_id":"p1","batch_id":"b1","files":[{"path":"wp-content/themes/x/style.css","content":"/*x*/"}],"completed":true}'


def test_extract_json_direct():
    data = extract_json(VALID_JSON)
    assert data["project_id"] == "p1"


def test_extract_json_fenced():
    text = f"متن مقدمه\n```json\n{VALID_JSON}\n```\nپایان"
    data = extract_json(text)
    assert data["batch_id"] == "b1"


def test_extract_json_prose_around():
    text = "این پاسخ:\n" + VALID_JSON + "\nپایان."
    data = extract_json(text)
    assert data["project_id"] == "p1"


def test_extract_json_empty_raises():
    with pytest.raises(ParseError):
        extract_json("")


def test_extract_json_invalid_raises():
    with pytest.raises(ParseError):
        extract_json("not a json")


def test_validate_payload_ok():
    import json
    data = json.loads(VALID_JSON)
    result = validate_payload(data, "p1")
    assert result["completed"] is True
    assert len(result["valid_files"]) == 1
    assert result["errors"] == []


def test_validate_payload_project_mismatch():
    import json
    data = json.loads(VALID_JSON)
    result = validate_payload(data, "other")
    assert any("project_id" in e for e in result["errors"])


def test_validate_payload_files_not_list():
    with pytest.raises(ParseError):
        validate_payload({"files": "nope"}, "p1")


def test_validate_payload_missing_path():
    data = {"files": [{"content": "x"}]}
    result = validate_payload(data, "p1")
    assert any("path" in e for e in result["errors"])


def test_validate_payload_path_escape():
    data = {"files": [{"path": "../etc/passwd", "content": "x"}]}
    result = validate_payload(data, "p1")
    assert any("نامعتبر" in e for e in result["errors"])


def test_validate_payload_outside_allowed():
    data = {"files": [{"path": "random/x.txt", "content": "x"}]}
    result = validate_payload(data, "p1")
    assert any("خارج از محدوده" in e for e in result["errors"])


def test_validate_payload_duplicate():
    data = {"files": [
        {"path": "wp-content/a.txt", "content": "1"},
        {"path": "wp-content/a.txt", "content": "2"},
    ]}
    result = validate_payload(data, "p1")
    assert any("تکراری" in e for e in result["errors"])
    assert len(result["valid_files"]) == 1


def test_validate_payload_completed_false():
    data = {"files": [], "completed": False}
    result = validate_payload(data, "p1")
    assert result["completed"] is False