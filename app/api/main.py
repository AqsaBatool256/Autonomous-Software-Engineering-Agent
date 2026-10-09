from fastapi import FastAPI, HTTPException
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
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/agent/analyze")
def analyze(request: AnalyzeTaskRequest):
    try:
        return analyze_task(
            task=request.task,
            workspace=request.workspace,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/agent/preview")
def preview(request: PreviewChangeRequest):
    try:
        return generate_change_preview(
            task=request.task,
            relative_path=request.relative_path,
            workspace=request.workspace,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
