import hashlib

import pytest

from app.tools.patch_applier import apply_code_proposal


def test_rejects_changes_without_approval(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    with pytest.raises(PermissionError, match="explicit approval"):
        apply_code_proposal(
            relative_path="calculator.py",
            proposed_code="def add(a, b):\n    return a + b + 1\n",
            approved=False,
            workspace=str(workspace),
        )

    assert target.read_text(encoding="utf-8") == original


def test_applies_change_after_approval(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    target.write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )

    proposed = "def add(a, b):\n    return a + b + 1\n"

    result = apply_code_proposal(
        relative_path="calculator.py",
        proposed_code=proposed,
        approved=True,
        workspace=str(workspace),
    )

    assert result["applied"] is True
    assert target.read_text(encoding="utf-8") == proposed
    assert result["sha256"] == hashlib.sha256(proposed.encode("utf-8")).hexdigest()


def test_rejects_path_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    outside_file = tmp_path / "outside.py"
    outside_file.write_text("secret = True\n", encoding="utf-8")

    with pytest.raises(ValueError):
        apply_code_proposal(
            relative_path="../outside.py",
            proposed_code="secret = False\n",
            approved=True,
            workspace=str(workspace),
        )

    assert outside_file.read_text(encoding="utf-8") == "secret = True\n"


def test_rejects_non_python_file(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with pytest.raises(ValueError, match="Only Python files"):
        apply_code_proposal(
            relative_path="README.md",
            proposed_code="Updated",
            approved=True,
            workspace=str(workspace),
        )


def test_rejects_stale_proposal(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    original_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

    # Simulate someone changing the file after the proposal was created.
    target.write_text(
        "def add(a, b):\n    return a + b + 10\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="proposal was created"):
        apply_code_proposal(
            relative_path="calculator.py",
            proposed_code="def add(a, b):\n    return a + b + 1\n",
            approved=True,
            workspace=str(workspace),
            expected_sha256=original_hash,
        )

    # The newer file contents must be preserved.
    assert target.read_text(encoding="utf-8") == (
        "def add(a, b):\n    return a + b + 10\n"
    )
