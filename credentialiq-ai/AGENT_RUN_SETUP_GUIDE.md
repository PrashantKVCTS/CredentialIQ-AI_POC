# CredentialIQ AI POC - Local Laptop Setup & Agent Execution Guide

This document provides a step-by-step, zero-error setup and execution guide to run **CredentialIQ AI POC** locally on your laptop (macOS, Windows, or Linux) after importing/cloning from GitHub.

---

## Quick Reference Summary

| Stage | Command | Goal |
| :--- | :--- | :--- |
| **1. Import & Setup** | `git clone <repo-url> && cd credentialiq-ai` | Clone repository |
| **2. Environment** | `bash scripts/setup.sh` | Create `.venv` & install dependencies |
| **3. Validation** | `ruff check app tests && mypy app` | Confirm code quality & typing |
| **4. Testing** | `pytest -v --cov=app tests/` | Run 18 unit & integration tests |
| **5. Start Server** | `bash scripts/run.sh` | Launch API at `http://localhost:8000` |
| **6. Smoke Test** | `python scripts/smoke_test.py` | Verify 8 API endpoints end-to-end |

---

## 1. Prerequisites & Laptop Requirements

Before starting, ensure your local machine has the following tools installed:

1. **Python 3.11 or later**:
   - Check version: `python3 --version` (or `python --version` on Windows)
2. **Git**:
   - Check version: `git --version`
3. **Visual Studio Code (Recommended)**:
   - Install **Python Extension** (`ms-python.python`)
   - Install **Pylance Extension** (`ms-python.vscode-pylance`)

---

## Step 1: Import Project from GitHub

Open your terminal or PowerShell and run:

```bash
# Clone the repository from GitHub
git clone <YOUR-GITHUB-REPOSITORY-URL> credentialiq-ai

# Navigate into the project directory
cd credentialiq-ai
```

### Verify Project Structure
Ensure the following core directories exist:
```
credentialiq-ai/
├── app/                  # Agent pipeline, API routes, models, services
├── knowledge/            # Synthetic compliance policy rules
├── samples/              # Intake test case JSON payloads
├── scripts/              # Setup, run, and smoke test bash/python scripts
├── tests/                # Pytest unit and integration test suite
├── .env.example          # Environment variables template
├── pyproject.toml        # Ruff, mypy, pytest configuration
└── requirements.txt      # Python dependency list
```

---

## Step 2: Virtual Environment Setup & Dependency Installation

### Option A: Automated One-Line Setup (Recommended)

Run the included automated setup script:
```bash
bash scripts/setup.sh
```

---

### Option B: Manual Setup (Step-by-Step)

#### 1. Create Virtual Environment
Use `--system-site-packages` so `pip` reuses pre-built system C-binary wheels (preventing long compilation for heavy libraries like `numpy` or `scikit-learn`):

- **macOS / Linux**:
  ```bash
  python3 -m venv --system-site-packages .venv
  ```
- **Windows (PowerShell)**:
  ```powershell
  python -m venv --system-site-packages .venv
  ```

#### 2. Activate Virtual Environment
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

#### 3. Upgrade Pip & Install Dependencies
```bash
pip install --upgrade pip
pip install --prefer-binary -r requirements.txt
```

#### 4. Create Environment Configuration File
Copy the sample environment file:
- **macOS / Linux**:
  ```bash
  cp .env.example .env
  ```
- **Windows**:
  ```cmd
  copy .env.example .env
  ```

Default `.env` contents:
```env
LLM_PROVIDER=deterministic
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
DATABASE_URL=sqlite:///./credentialiq.db
LOG_LEVEL=INFO
KNOWLEDGE_DIR=./knowledge
```

---

## Step 3: Run Static Type & Linting Validation

Verify that the code is free of syntax, formatting, and static typing errors:

### 1. Run Ruff Linter
```bash
ruff check app tests
```
*Expected output*: `All checks passed!`

### 2. Run Mypy Type Checker
```bash
mypy app
```
*Expected output*: `Success: no issues found in 46 source files`

---

## Step 4: Run Unit and Integration Tests

Execute the full automated Pytest test suite with code coverage:

```bash
pytest -v --cov=app tests/
```

**Expected Result**:
```
======================= 18 passed in 0.38s =======================
TOTAL Coverage: 88%
```

---

## Step 5: Start the Agent & Web API Server

Launch the web API server locally on port 8000:

### Option A: Using Runner Script
```bash
bash scripts/run.sh
```

### Option B: Direct Uvicorn Command
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Access Interactive API Documentation
Once running, open your browser to:
- **Swagger UI Interactive API**: `http://127.0.0.1:8000/docs`
- **ReDoc UI**: `http://127.0.0.1:8000/redoc`
- **Health Check Endpoint**: `http://127.0.0.1:8000/health`

---

## Step 6: Execute API Smoke Tests & Test Cases

Keep the server running in Terminal 1. Open Terminal 2 (with `.venv` activated) to execute tests:

### 1. Automated API Smoke Test Script
```bash
python scripts/smoke_test.py
```
**Expected Result**: `ALL API SMOKE TESTS PASSED SUCCESSFULLY! (100%)`

---

### 2. Manual Test Case Execution via `curl`

#### Case Test 1: Clean Provider Intake (Expected Decision: `AutoApprove`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/cases/process" \
  -H "Content-Type: application/json" \
  -d @samples/clean_provider_case.json
```

#### Case Test 2: Exception Provider Intake (Expected Decision: `CommitteeReview`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/cases/process" \
  -H "Content-Type: application/json" \
  -d @samples/exception_provider_case.json
```

#### Case Test 3: Hold Provider Intake with Active Suspension (Expected Decision: `Deny`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/cases/process" \
  -H "Content-Type: application/json" \
  -d @samples/hold_provider_case.json
```

#### Case Test 4: Apply Human Reviewer Override
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/cases/<CASE_ID_HERE>/override" \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer_id": "DrSmith",
    "override_decision": "Approved",
    "rationale": "Granted special waiver based on clean 5-year history."
  }'
```

#### Case Test 5: Retrieve Audit Trail
```bash
curl "http://127.0.0.1:8000/api/v1/cases/<CASE_ID_HERE>/audit-trail"
```

---

## Step 7: (Optional) Enabling Gemini LLM

By default, the application runs offline in **Deterministic Mode** using safety-critical compliance rule logic.

To enable official Google Gemini API integration:

1. Obtain a Gemini API Key from Google AI Studio.
2. Open `.env` and set:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. Restart the server (`bash scripts/run.sh`).
4. If network failure or API throttling occurs, the system automatically falls back to deterministic logic without crashing.

---

## Step 8: Troubleshooting & Zero-Error Solutions

### 1. Script Permission Errors (`Permission denied`)
If bash scripts fail to execute:
```bash
chmod +x scripts/setup.sh scripts/run.sh
```

### 2. Port 8000 Address Already in Use
If port 8000 is occupied by another application:
- Kill process occupying port 8000 (Linux/macOS):
  ```bash
  fuser -k 8000/tcp || true
  ```
- Or run Uvicorn on port 8080:
  ```bash
  uvicorn app.main:app --port 8080
  ```

### 3. VS Code / Pylance "Import Could Not Be Resolved"
- Open VS Code Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
- Select `Python: Select Interpreter`.
- Choose the interpreter inside `./.venv/bin/python`.

---

## Complete Verification Checklist

- [x] Python 3.11+ environment created (`.venv`)
- [x] Dependencies installed without error
- [x] Configuration (`.env`) loaded
- [x] `ruff check` passed (0 errors)
- [x] `mypy app` passed (0 type errors)
- [x] `pytest` passed (18 tests, 88% coverage)
- [x] Server listening on `http://127.0.0.1:8000`
- [x] API smoke test passed (100%)
