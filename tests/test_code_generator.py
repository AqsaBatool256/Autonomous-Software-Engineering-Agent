import pytest

from app.services import code_generator


def test_generate_code_proposal_returns_code_without_applying(
    monkeypatch,
):
    class FakeResponse:
        text = "def add(a, b):\n    return a + b\n"

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.models = FakeModels()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        code_generator.genai,
        "Client",
        FakeClient,
    )

    result = code_generator.generate_code_proposal(
        task="Keep the addition function unchanged",
        relative_path="calculator.py",
    )

    assert result["file"] == "calculator.py"
    assert "def add(a, b):" in result["proposed_code"]
    assert result["applied"] is False


def test_generate_code_proposal_rejects_empty_task():
    with pytest.raises(ValueError, match="Task must not be empty"):
        code_generator.generate_code_proposal(
            task="   ",
            relative_path="calculator.py",
        )


def test_generate_code_proposal_rejects_non_python_file():
    with pytest.raises(ValueError, match="Only Python files"):
        code_generator.generate_code_proposal(
            task="Update this file",
            relative_path="README.md",
        )
