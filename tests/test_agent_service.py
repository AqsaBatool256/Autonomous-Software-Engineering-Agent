import hashlib

import pytest

from app.services import agent_service


def test_preview_code_change_returns_diff(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    proposed = "def add(a, b):\n    return a + b + 1\n"

    result = agent_service.preview_code_change(
        relative_path="calculator.py",
        proposed_code=proposed,
        workspace=str(workspace),
    )

    assert result["changed"] is True
    assert "return a + b + 1" in result["patch"]
    assert result["applied"] is False
    assert (
        result["original_sha256"]
        == hashlib.sha256(original.encode("utf-8")).hexdigest()
    )


def test_preview_does_not_modify_original_file(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    agent_service.preview_code_change(
        relative_path="calculator.py",
        proposed_code="def add(a, b):\n    return a + b + 1\n",
        workspace=str(workspace),
    )

    assert target.read_text(encoding="utf-8") == original


def test_generate_change_preview_does_not_apply_changes(
    tmp_path,
    monkeypatch,
):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    original_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

    def fake_generate_code_proposal(
        task,
        relative_path,
        workspace,
    ):
        return {
            "file": relative_path,
            "original_code": original,
            "original_sha256": original_hash,
            "proposed_code": ("def add(a, b):\n    return a + b + 1\n"),
            "applied": False,
        }

    monkeypatch.setattr(
        agent_service,
        "generate_code_proposal",
        fake_generate_code_proposal,
    )

    result = agent_service.generate_change_preview(
        task="Change the addition behavior",
        relative_path="calculator.py",
        workspace=str(workspace),
    )

    assert result["changed"] is True
    assert "return a + b + 1" in result["patch"]
    assert result["original_sha256"] == original_hash
    assert result["applied"] is False

    # Generating a preview must never modify the source file.
    assert target.read_text(encoding="utf-8") == original


def test_apply_approved_change_requires_approval(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    original_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

    with pytest.raises(PermissionError, match="explicit approval"):
        agent_service.apply_approved_change(
            relative_path="calculator.py",
            proposed_code="def add(a, b):\n    return a + b + 1\n",
            original_sha256=original_hash,
            approved=False,
            workspace=str(workspace),
        )

    assert target.read_text(encoding="utf-8") == original


def test_apply_approved_change_applies_approved_proposal(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    original_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

    proposed = "def add(a, b):\n    return a + b + 1\n"

    result = agent_service.apply_approved_change(
        relative_path="calculator.py",
        proposed_code=proposed,
        original_sha256=original_hash,
        approved=True,
        workspace=str(workspace),
    )

    assert result["applied"] is True
    assert target.read_text(encoding="utf-8") == proposed


def test_apply_approved_change_rejects_stale_proposal(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    original = "def add(a, b):\n    return a + b\n"
    target.write_text(original, encoding="utf-8")

    original_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

    # Simulate a change after the proposal was generated.
    newer_content = "def add(a, b):\n    return a + b + 10\n"
    target.write_text(newer_content, encoding="utf-8")

    with pytest.raises(RuntimeError, match="changed after the proposal"):
        agent_service.apply_approved_change(
            relative_path="calculator.py",
            proposed_code="def add(a, b):\n    return a + b + 1\n",
            original_sha256=original_hash,
            approved=True,
            workspace=str(workspace),
        )

    assert target.read_text(encoding="utf-8") == newer_content
