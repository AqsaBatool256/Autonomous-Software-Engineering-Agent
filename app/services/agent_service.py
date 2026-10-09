import hashlib
from pathlib import Path

from app.core.task_planner import create_ai_plan
from app.services.code_generator import generate_code_proposal
from app.tools.codebase_analyzer import (
    list_project_files,
    read_project_file,
)
from app.tools.patch_applier import apply_code_proposal
from app.tools.patch_generator import generate_patch


def analyze_task(
    task: str,
    workspace: str = "workspace/sample_calculator",
) -> dict:
    """Inspect a project and prepare an engineering plan."""

    if not task.strip():
        raise ValueError("Task must not be empty.")

    root = Path(workspace).resolve()
    files = list_project_files(str(root))

    source_files = []

    for relative_path in files:
        if not relative_path.endswith(".py"):
            continue

        try:
            result = read_project_file(str(root), relative_path)
            source_files.append(result)
        except (ValueError, FileNotFoundError):
            continue

    if not source_files:
        raise ValueError("No readable Python source files were found in the workspace.")

    source_summary = "\n\n".join(
        f"File: {item['path']}\n{item['content']}" for item in source_files
    )

    contextual_task = f"""
User's requested task:
{task}

Inspected project files:
{source_summary}

Create a plan specifically for this codebase.
Identify the actual files relevant to the task.
Do not claim that you have modified or tested any files.
"""

    plan = create_ai_plan(contextual_task)

    return {
        "task": task,
        "workspace": str(root),
        "files_found": files,
        "plan": plan.model_dump(),
    }


def preview_code_change(
    relative_path: str,
    proposed_code: str,
    workspace: str = "workspace/sample_calculator",
) -> dict:
    """Preview a code change without modifying the original file."""

    if not relative_path.endswith(".py"):
        raise ValueError("Only Python files can be previewed.")

    root = Path(workspace).resolve()
    original = read_project_file(str(root), relative_path)
    original_code = original["content"]

    original_sha256 = hashlib.sha256(original_code.encode("utf-8")).hexdigest()

    patch = generate_patch(
        original_code=original_code,
        proposed_code=proposed_code,
        filename=relative_path,
    )

    return {
        "file": relative_path,
        "patch": patch,
        "changed": bool(patch),
        "original_sha256": original_sha256,
        "applied": False,
    }


def generate_change_preview(
    task: str,
    relative_path: str,
    workspace: str = "workspace/sample_calculator",
) -> dict:
    """Generate an AI proposal and return its reviewable patch."""

    if not task.strip():
        raise ValueError("Task must not be empty.")

    proposal = generate_code_proposal(
        task=task,
        relative_path=relative_path,
        workspace=workspace,
    )

    preview = preview_code_change(
        relative_path=relative_path,
        proposed_code=proposal["proposed_code"],
        workspace=workspace,
    )

    # Use the fingerprint captured when the AI proposal was generated.
    return {
        "task": task,
        "file": relative_path,
        "patch": preview["patch"],
        "changed": preview["changed"],
        "original_sha256": proposal["original_sha256"],
        "applied": False,
    }


def apply_approved_change(
    relative_path: str,
    proposed_code: str,
    original_sha256: str,
    approved: bool,
    workspace: str = "workspace/sample_calculator",
) -> dict:
    """Apply a reviewed proposal only after approval and stale-file checks."""

    if not original_sha256:
        raise ValueError("The proposal's original SHA-256 fingerprint is required.")

    result = apply_code_proposal(
        relative_path=relative_path,
        proposed_code=proposed_code,
        approved=approved,
        workspace=workspace,
        expected_sha256=original_sha256,
    )

    return result
