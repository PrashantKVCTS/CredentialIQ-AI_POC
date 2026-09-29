# CredentialIQ AI POC - Manual Setup, Verification & Debugging Guide

This guide provides step-by-step instructions to manually replicate the environment setup, dependency installation, static validation, test execution, API server launch, API smoke testing, and troubleshooting/debugging procedures for **CredentialIQ AI POC**.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step 1: Virtual Environment & Dependencies](#step-1-virtual-environment--dependencies)
3. [Step 2: Static Validation & Code Formatting](#step-2-static-validation--code-formatting)
4. [Step 3: Running Automated Tests](#step-3-running-automated-tests)
5. [Step 4: Launching the API Server](#step-4-launching-the-api-server)
6. [Step 5: Executing API Smoke Tests & Manual Calls](#step-5-executing-api-smoke-tests--manual-calls)
7. [Step 6: Comprehensive Troubleshooting & Debugging Guide](#step-6-comprehensive-troubleshooting--debugging-guide)

---

## 1. Prerequisites

Ensure your system meets the following requirements:
- **Operating System**: Linux / macOS / Windows Subsystem for Linux (WSL)
- **Python**: Python 3.11 or later (`python3 --version`)
- **Git & Bash Shell**
- **Visual Studio Code** (with Microsoft Python and Pylance extensions)

---

## Step 1: Virtual Environment & Dependencies

### 1.1 Navigate to Project Directory
```bash
cd /config/.gemini/antigravity/scratch/credentialiq-ai
```

### 1.2 Create Python Virtual Environment
Use `--system-site-packages` to allow pip to leverage pre-installed system binary wheels for heavy libraries (such as `numpy` and `scikit-learn`), avoiding long C-extension compilation:
```bash
python3 -m venv --system-site-packages .venv
```

### 1.3 Activate Virtual Environment
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

### 1.4 Upgrade Pip and Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.5 Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration:
```env
LLM_PROVIDER=deterministic
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
DATABASE_URL=sqlite:///./credentialiq.db
LOG_LEVEL=INFO
KNOWLEDGE_DIR=./knowledge
```

Alternatively, run the automated setup script:
```bash
bash scripts/setup.sh
```

---

## Step 2: Static Validation & Code Formatting

### 2.1 Run Ruff Linting & Formatting Check
```bash
ruff check app tests
```
*To automatically fix formatting or safe import order issues:*
```bash
ruff check --fix app tests
```

### 2.2 Run Mypy Static Type Checking
```bash
mypy app
```
**Expected Output:**
```
Success: no issues found in 46 source files
```

---

## Step 3: Running Automated Tests

Run unit and integration tests with coverage reporting using Pytest:

```bash
pytest -v --cov=app tests/
```

**Expected Output Summary:**
```
tests/test_agents.py::test_credential_verification_agent PASSED
tests/test_agents.py::test_license_verification_agent PASSED
tests/test_agents.py::test_workflow_agent_clean PASSED
tests/test_agents.py::test_workflow_agent_hold PASSED
tests/test_connectors.py::test_mock_license_connector_clean PASSED
tests/test_connectors.py::test_mock_license_connector_suspended PASSED
tests/test_connectors.py::test_mock_sanction_connector_clear PASSED
tests/test_connectors.py::test_mock_sanction_connector_match PASSED
tests/test_orchestration.py::test_orchestrator_clean_case PASSED
tests/test_orchestration.py::test_orchestrator_hold_case PASSED
tests/test_api.py::test_health_endpoints PASSED
tests/test_api.py::test_system_info_and_rag PASSED
tests/test_api.py::test_process_case_and_override PASSED
tests/test_rag.py::test_rag_repository_search PASSED
tests/test_services.py::test_pii_sanitizer PASSED
tests/test_services.py::test_deterministic_llm_clean PASSED
tests/test_services.py::test_deterministic_llm_hold PASSED

================------- 18 passed in 0.40s =======================
TOTAL Coverage: 88%
```

---

## Step 4: Launching the API Server

### 4.1 Launch Uvicorn Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Or execute the runner script:
```bash
bash scripts/run.sh
```

### 4.2 Verify Server Operations
- **Server URL**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **ReDoc UI**: `http://127.0.0.1:8000/redoc`

---

## Step 5: Executing API Smoke Tests & Manual Calls

### 5.1 Automated Smoke Test Script
In a separate terminal (with `.venv` activated):
```bash
python scripts/smoke_test.py
```

### 5.2 Manual API Requests using `curl`

#### A. Health Check
```bash
curl -s http://127.0.0.1:8000/health | jq .
```
**Expected Response:**
```json
{
  "status": "healthy",
  "app_name": "CredentialIQ AI POC",
  "version": "1.0.0",
  "timestamp_utc": "2026-09-29T11:50:00Z"
}
```

#### B. Search Compliance RAG Repository
```bash
curl -s "http://127.0.0.1:8000/api/v1/system/rag/search?q=NCQA%20license" | jq .
```

#### C. Process Clean Provider Intake Case
```bash
curl -s -X POST "http://127.0.0.1:8000/api/v1/cases/process" \
  -H "Content-Type: application/json" \
  -d @samples/clean_provider_case.json | jq .
```
**Key Response Fields:**
- `"status": "Clean"`
- `"recommendation": "AutoApprove"`

#### D. Process Hold Provider Intake Case (Suspended License)
```bash
curl -s -X POST "http://127.0.0.1:8000/api/v1/cases/process" \
  -H "Content-Type: application/json" \
  -d @samples/hold_provider_case.json | jq .
```
**Key Response Fields:**
- `"status": "Hold"`
- `"recommendation": "Deny"`

#### E. Apply Reviewer Override
```bash
curl -s -X POST "http://127.0.0.1:8000/api/v1/cases/<CASE_ID>/override" \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer_id": "DrSmith",
    "override_decision": "Approved",
    "rationale": "Special committee waiver granted."
  }' | jq .
```

#### F. Fetch Case Audit Trail
```bash
curl -s "http://127.0.0.1:8000/api/v1/cases/<CASE_ID>/audit-trail" | jq .
```

---

## Step 6: Comprehensive Troubleshooting & Debugging Guide

### Issue 1: `pip install` hangs or compiles `scikit-learn`/`numpy` from source tar.gz
- **Symptom**: `pip install` gets stuck at `Preparing metadata (pyproject.toml) ...` or `Installing build dependencies ...`.
- **Root Cause**: Python pre-release versions or environment mismatches cause pip to attempt compiling C/C++ extensions from source tar.gz.
- **Solution**:
  1. Create virtual environment with `--system-site-packages`:
     ```bash
     rm -rf .venv
     python3 -m venv --system-site-packages .venv
     source .venv/bin/activate
     ```
  2. Use `--prefer-binary` during installation:
     ```bash
     pip install --prefer-binary -r requirements.txt
     ```

---

### Issue 2: `sqlite3.OperationalError: no such table: cases`
- **Symptom**: Database queries fail with missing table errors.
- **Root Cause**: SQLite in-memory databases (`sqlite:///:memory:`) create a new isolated database instance per connection unless pooled.
- **Solution**:
  - In application code, `init_db()` is called automatically on FastAPI startup (`app/main.py`).
  - For testing fixtures in `tests/conftest.py`, use `StaticPool` and `check_same_thread=False`:
    ```python
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ```

---

### Issue 3: `TypeError: Object of type datetime is not JSON serializable`
- **Symptom**: Saving cases or audit events throws SQLAlchemy statement errors when dumping JSON columns containing `datetime.utcnow()` timestamps.
- **Root Cause**: Python's built-in `json.dumps()` cannot serialize native `datetime` objects.
- **Solution**:
  - Configure SQLAlchemy `create_engine` with `json_serializer`:
    ```python
    import json

    engine = create_engine(
        settings.DATABASE_URL,
        json_serializer=lambda obj: json.dumps(obj, default=str),
    )
    ```

---

### Issue 4: Uvicorn Error `[Errno 98] Address already in use` (Port 8000 Conflict)
- **Symptom**: `uvicorn` fails to start because port 8000 is occupied.
- **Solution**:
  1. Find and terminate the process occupying port 8000:
     ```bash
     fuser -k 8000/tcp || true
     ```
  2. Or launch Uvicorn on an alternative port (e.g., 8080):
     ```bash
     uvicorn app.main:app --port 8080
     ```

---

### Issue 5: Gemini API Fallback / Missing API Key
- **Symptom**: Logs show `Gemini API evaluation failed or timed out. Falling back to deterministic model.`
- **Root Cause**: `GEMINI_API_KEY` is not set or network egress to Gemini API is restricted.
- **Solution**:
  - The system is built with a resilient fallback mechanism. It will automatically use `DeterministicLanguageModelService` without failing.
  - To enable Gemini API:
    1. Set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=your_key_here` in `.env`.
    2. Verify package `google-genai` is installed:
       ```bash
       python -c "from google import genai; print(genai.__file__)"
       ```

---

### Issue 6: Ruff or Mypy Type Checker Errors in VS Code / Pylance
- **Symptom**: VS Code displays red squigglies under imports or type annotations.
- **Solution**:
  1. Ensure the Python interpreter is set to `.venv`:
     - Press `Ctrl+Shift+P` -> `Python: Select Interpreter` -> Select `./.venv/bin/python`.
  2. Verify settings in `.vscode/settings.json`:
     ```json
     {
       "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
       "python.analysis.extraPaths": ["${workspaceFolder}"],
       "python.analysis.typeCheckingMode": "basic"
     }
     ```

---

### Summary Checklist

| Action | Command | Expected Outcome |
| :--- | :--- | :--- |
| **Setup** | `bash scripts/setup.sh` | `.venv` created & dependencies installed |
| **Lint** | `ruff check app tests` | All checks passed |
| **Type Check** | `mypy app` | Success: no issues found |
| **Test** | `pytest -v --cov=app tests/` | 18 passed (88% coverage) |
| **Run** | `bash scripts/run.sh` | Server running at `http://127.0.0.1:8000` |
| **Smoke Test** | `python scripts/smoke_test.py` | 100% smoke tests passed |
