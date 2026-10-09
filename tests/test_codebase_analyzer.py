import pytest

from app.tools.codebase_analyzer import read_project_file


def test_read_existing_calculator_file():
    result = read_project_file(
        "workspace/sample_calculator",
        "calculator.py",
    )

    assert "def add" in result["content"]
    assert "def divide" in result["content"]


def test_reject_path_outside_workspace():
    with pytest.raises(ValueError):
        read_project_file(
            "workspace/sample_calculator",
            "../../.env",
        )


def test_reject_missing_file():
    with pytest.raises(FileNotFoundError):
        read_project_file(
            "workspace/sample_calculator",
            "missing_file.py",
        )
