import os
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from app.services.agent_service import (
    analyze_task,
    generate_change_preview,
)


app = FastAPI(
    title="Autonomous Software Engineering Agent",
    description=(
        "An AI-powered assistant that analyzes software tasks, "
        "generates code proposals, and previews changes for review."
    ),
    version="1.0.0",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_WORKSPACE = (PROJECT_ROOT / "workspace" / "sample_calculator").resolve()

# Adds the Authorize button to Swagger UI.
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def require_api_key(
    x_api_key: str | None = Security(api_key_header),
) -> None:
    """Require a configured API key for AI endpoints."""

    expected_key = os.getenv("APP_API_KEY", "")

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="API access is not configured.",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )


def validate_workspace(workspace: str) -> str:
    """Allow access only to the designated sample workspace."""

    requested_path = Path(workspace)

    if requested_path.is_absolute():
        candidate = requested_path.resolve()
    else:
        candidate = (PROJECT_ROOT / requested_path).resolve()

    if candidate != SAMPLE_WORKSPACE:
        raise HTTPException(
            status_code=400,
            detail="Only the designated sample workspace is allowed.",
        )

    if not SAMPLE_WORKSPACE.is_dir():
        raise HTTPException(
            status_code=500,
            detail="The sample workspace is unavailable.",
        )

    return str(SAMPLE_WORKSPACE)


class AnalyzeTaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=5000)
    workspace: str = Field(
        default="workspace/sample_calculator",
        min_length=1,
        max_length=500,
    )


class PreviewChangeRequest(BaseModel):
    task: str = Field(min_length=1, max_length=5000)
    relative_path: str = Field(min_length=1, max_length=500)
    workspace: str = Field(
        default="workspace/sample_calculator",
        min_length=1,
        max_length=500,
    )


@app.get("/")
def home():
    return {
        "message": "Autonomous Software Engineering Agent API",
        "docs": "/docs",
        "health": "/health",
        "authentication": ("X-API-Key required for AI endpoints"),
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/agent/analyze",
    dependencies=[Depends(require_api_key)],
)
def analyze(request: AnalyzeTaskRequest):
    workspace = validate_workspace(request.workspace)

    try:
        return analyze_task(
            task=request.task,
            workspace=workspace,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post(
    "/agent/preview",
    dependencies=[Depends(require_api_key)],
)
def preview(request: PreviewChangeRequest):
    workspace = validate_workspace(request.workspace)

    try:
        return generate_change_preview(
            task=request.task,
            relative_path=request.relative_path,
            workspace=workspace,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
