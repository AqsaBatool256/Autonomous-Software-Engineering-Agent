from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
}

MAX_FILE_BYTES = 200_000
MAX_FILES = 200


def _resolve_workspace(workspace: str) -> Path:
    """Resolve and validate the designated workspace directory."""

    root = Path(workspace).resolve(strict=True)

    if not root.is_dir():
        raise ValueError("Workspace must be an existing directory.")

    return root


def list_project_files(workspace: str) -> list[str]:
    """List inspectable files without following symbolic links."""

    root = _resolve_workspace(workspace)
    files = []

    for path in root.rglob("*"):
        relative = path.relative_to(root)

        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue

        # Do not traverse or include symbolic links.
        if path.is_symlink():
            continue

        if not path.is_file():
            continue

        files.append(relative.as_posix())

        if len(files) >= MAX_FILES:
            break

    return sorted(files)


def read_project_file(
    workspace: str,
    relative_path: str,
) -> dict:
    """Read a UTF-8 text file confined to the workspace."""

    root = _resolve_workspace(workspace)
    supplied_path = Path(relative_path)

    if supplied_path.is_absolute():
        raise ValueError("Absolute file paths are not allowed.")

    if any(part in IGNORED_DIRECTORIES for part in supplied_path.parts):
        raise ValueError("This directory is excluded from inspection.")

    target = root / supplied_path

    # Check each path component before resolving the final target.
    current = root

    for part in supplied_path.parts:
        if part in ("", ".", ".."):
            if part == "..":
                raise ValueError("Parent-directory traversal is not allowed.")
            continue

        current = current / part

        if current.is_symlink():
            raise ValueError("Symbolic links are not allowed.")

    if not target.exists():
        raise FileNotFoundError("The requested project file was not found.")

    if not target.is_file():
        raise ValueError("The requested path is not a regular file.")

    resolved_target = target.resolve(strict=True)

    if not resolved_target.is_relative_to(root):
        raise ValueError("Access outside the workspace is not allowed.")

    if resolved_target.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("The file is too large to inspect.")

    try:
        content = resolved_target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Only UTF-8 text files can be inspected.") from exc

    return {
        "path": supplied_path.as_posix(),
        "characters": len(content),
        "content": content,
    }
