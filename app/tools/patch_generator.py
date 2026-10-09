import difflib


def generate_patch(
    original_code: str,
    proposed_code: str,
    filename: str = "calculator.py",
) -> str:
    """Generate a unified diff without modifying any files."""

    original_lines = original_code.splitlines(keepends=True)
    proposed_lines = proposed_code.splitlines(keepends=True)

    patch = difflib.unified_diff(
        original_lines,
        proposed_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )

    return "".join(patch)
