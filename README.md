# Autonomous Software Engineering Agent

An AI-powered software engineering assistant built with Python, FastAPI, and Google's Gemini API. It can analyze coding tasks, inspect a project workspace, generate proposed code changes, preview unified diffs, and apply changes only after explicit approval.

## Features

- **AI Task Planning:** Creates structured implementation plans for software engineering tasks.
- **Codebase Analysis:** Inspects files within a specified workspace.
- **AI Code Generation:** Generates proposed Python code changes without immediately modifying the original file.
- **Diff Preview:** Shows proposed changes as a unified diff.
- **Explicit Approval:** Requires approval before applying a proposed code change.
- **Stale-Change Protection:** Uses SHA-256 fingerprints to help prevent applying a proposal to a file that has changed since it was reviewed.
- **REST API:** Provides endpoints through FastAPI.
- **Automated Tests:** Includes tests for planning, code generation, analysis, and patch application.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Google Gemini API
- Pydantic
- Pytest

## Project Structure

```text
Autonomous-Software-Engineering-Agent/
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── tools/
│   └── frontend/
├── tests/
├── workspace/
│   └── sample_calculator/
├── logs/
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Autonomous-Software-Engineering-Agent
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the repository URL after publishing this project.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a `.env` file in the project root with your own key:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit your `.env` file or expose your API key publicly.

### 5. Start the API server

```bash
uvicorn app.api.main:app --reload
```

Open the interactive API documentation:

- http://127.0.0.1:8000/docs

Health check:

- http://127.0.0.1:8000/health

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic API information |
| GET | `/health` | Health check |
| POST | `/agent/analyze` | Analyze a task and generate a plan |
| POST | `/agent/preview` | Generate a proposed code change and preview its diff |

## Run Tests

Run the complete test suite:

```bash
python -m pytest -q
```

## Safety and Design

The agent separates code generation from code application. Proposed changes can be reviewed before being applied, and the patch application utility requires explicit approval and checks the original file fingerprint.

AI-generated code should always be reviewed and tested. Explicit approval and hash checks are safeguards, not a guarantee that every change is safe or correct. Run this project only in workspaces you are authorized to modify.

## Current Status

The core planning, code analysis, code generation, patch preview, approval safeguards, and automated tests have been implemented. Further work can expand the agent with additional engineering tools, a user interface, and public deployment.

## Author

**Aqsa Batool Saqib**

- GitHub: [AqsaBatool256](https://github.com/AqsaBatool256)
- LinkedIn: [Aqsa Batool Saqib](https://www.linkedin.com/in/aqsabatoolsaqib/)

---

Built as a portfolio project exploring AI-assisted software engineering.
