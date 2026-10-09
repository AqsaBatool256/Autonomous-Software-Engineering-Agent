from app.tools.patch_generator import generate_patch


def test_patch_shows_code_changes():
    original = "def add(a, b):\n    return a + b\n"
    proposed = "def add(a, b):\n    return a + b + 1\n"

    patch = generate_patch(original, proposed)

    assert "--- a/calculator.py" in patch
    assert "+++ b/calculator.py" in patch
    assert "-    return a + b" in patch
    assert "+    return a + b + 1" in patch


def test_patch_does_not_change_original_code():
    original = "def add(a, b):\n    return a + b\n"
    proposed = "def add(a, b):\n    return a + b + 1\n"

    generate_patch(original, proposed)

    assert original == "def add(a, b):\n    return a + b\n"


def test_identical_code_produces_empty_patch():
    code = "def add(a, b):\n    return a + b\n"

    patch = generate_patch(code, code)

    assert patch == ""
