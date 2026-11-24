from core.helpers import slugify, checksum, human_size


def test_slugify_english():
    assert slugify("My Cool Project") == "my-cool-project"


def test_slugify_persian():
    assert slugify("فروشگاه دیجیتال") == "فروشگاه-دیجیتال"


def test_slugify_special_chars():
    assert slugify("Hello!@#$World") == "helloworld"


def test_slugify_empty():
    assert slugify("") == "project"
    assert slugify(None) == "project"


def test_slugify_underscore_and_spaces():
    assert slugify("a_b   c") == "a-b-c"


def test_checksum_deterministic():
    assert checksum("abc") == checksum("abc")
    assert checksum("abc") != checksum("abd")


def test_checksum_sha256_length():
    assert len(checksum("abc")) == 64


def test_human_size():
    assert human_size(500) == "500.0 B"
    assert "KB" in human_size(2048)
    assert "MB" in human_size(3 * 1024 * 1024)