import hashlib
import os
import tempfile
from pathlib import Path

from app.tools.codebase_analyzer import read_project_file


def _sha256(content: str) -> str:
    """Return a fingerprint of file contents."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def apply_code_proposal(
    relative_path: str,
    proposed_code: str,
    approved: bool,
    workspace: str = "workspace/sample_calculator",
    expected_sha256: str | None = None,
) -> dict:
    """Apply an approved proposal only if the original content is unchanged."""

    if not approved:
        raise PermissionError(
            "Code changes require explicit approval before application."
        )

    if not relative_path.endswith(".py"):
        raise ValueError("Only Python files can be modified.")

    if not isinstance(proposed_code, str):
        raise ValueError("Proposed code must be text.")

    root = Path(workspace).resolve(strict=True)
    original = read_project_file(str(root), relative_path)
    target = root / relative_path

    if target.is_symlink():
        raise ValueError("Symbolic links cannot be modified.")

    resolved_target = target.resolve(strict=True)

    if not resolved_target.is_relative_to(root):
        raise ValueError("Access outside the workspace is not allowed.")

    if not resolved_target.is_file():
        raise ValueError("The target must be a regular file.")

    current_content = resolved_target.read_text(encoding="utf-8")

    if current_content != original["content"]:
        raise RuntimeError(
            "The target file changed during inspection. Review it again."
        )

    if expected_sha256 is not None:
        if _sha256(current_content) != expected_sha256:
            raise RuntimeError(
                "The original file changed after the proposal was created. "
                "Generate and review a new proposal."
            )

    # Write to a temporary file in the same directory, then replace the target.
    # This reduces the chance of leaving a partially written file.
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=resolved_target.parent,
            prefix=".agent-proposal-",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(proposed_code)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        # Recheck immediately before replacement.
        if resolved_target.is_symlink():
            raise ValueError("Symbolic links cannot be modified.")

        if resolved_target.read_text(encoding="utf-8") != current_content:
            raise RuntimeError(
                "The target file changed before replacement. Review it again."
            )

        os.replace(temp_path, resolved_target)
        temp_path = None

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return {
        "file": relative_path,
        "applied": True,
        "message": "Approved code proposal applied.",
        "sha256": _sha256(proposed_code),
    }
