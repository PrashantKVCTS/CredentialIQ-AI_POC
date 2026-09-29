# CredentialIQ AI POC - Agentic Healthcare Credentialing

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)]()
[![Framework](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)]()
[![Orchestration](https://img.shields.io/badge/LangGraph-Agentic-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

> [!IMPORTANT]
> **POC Legal Disclaimer**: CredentialIQ AI is a proof-of-concept system utilizing simulated primary source connectors and synthetic policy rules. POC outputs do not constitute official credentialing determinations and require authorization by a qualified human credentialing committee.

---

## Overview

**CredentialIQ AI** is a fully functional Python proof of concept for healthcare provider credentialing and compliance. The platform automates provider intake, primary-source license verification, sanction screening, policy retrieval (via a local vector-like RAG repository using TF-IDF), AI risk assessment, and workflow recommendations—producing an immutable, UTC-timestamped audit trail in SQLite.

---

## Key Features

- **5 Specialized Agents**:
  1. `CredentialVerificationAgent`: Schema validation, identifier normalization, PII redaction.
  2. `LicenseVerificationAgent`: Simulated primary source state medical board verification (`is_simulated = True`).
  3. `SanctionCheckAgent`: Simulated OIG LEIE, SAM.gov, NPDB screening (`is_simulated = True`).
  4. `RiskAssessmentAgent`: Local RAG policy matching + LLM/Deterministic risk scoring (`Clean`, `Exception`, `Hold`).
  5. `WorkflowAgent`: Formulates recommendations (`AutoApprove`, `CommitteeReview`, `Deny`), action items, review dates.
- **LangGraph Workflow Orchestration**: State graph sequential pipeline execution with error recovery and persistence.
- **Dual LLM Architecture**: Operates offline with `DeterministicLanguageModelService` or connects to Gemini via official `google-genai` SDK when `GEMINI_API_KEY` is provided.
- **Local Policy RAG Repository**: Seeded synthetic NCQA, state law, and payer compliance rules indexed with `scikit-learn` TF-IDF.
- **Human Reviewer Overrides & Audit Trail**: Full support for reviewer overrides and immutable audit logging.
- **FastAPI REST API**: Asynchronous endpoints with Swagger UI at `/docs`.

---

## Quick Start Guide

### 1. Setup Virtual Environment
```bash
./scripts/setup.sh
```

### 2. Run Test Suite
```bash
source .venv/bin/activate
pytest --cov=app tests/
```

### 3. Run Web API Server
```bash
./scripts/run.sh
```
The API will launch at **`http://127.0.0.1:8000`**.  
Interactive Swagger documentation is at **`http://127.0.0.1:8000/docs`**.

### 4. Execute API Smoke Tests
In a separate terminal while the API is running:
```bash
source .venv/bin/activate
python scripts/smoke_test.py
```

---

## Environment Variables

Configure in `.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `deterministic` | Provider mode: `deterministic` or `gemini` |
| `GEMINI_API_KEY` | *(None)* | Optional Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `DATABASE_URL` | `sqlite:///./credentialiq.db` | SQLite connection string |

---

## Project Structure

```
credentialiq-ai/
    .vscode/            # Launch, settings, and task configurations
    app/
        api/            # FastAPI routes, dependencies, exception handlers, middleware
        agents/         # 5 specialized credentialing agents
        orchestration/  # LangGraph state definition, graph, and orchestrator
        core/           # Settings, enums, exceptions, logging, PII security
        models/         # SQLAlchemy domain models and SQLite session
        schemas/        # Pydantic request, response, and evidence schemas
        repositories/   # Case repository and local TF-IDF RAG repository
        connectors/     # Primary source mock state board & sanction connectors
        services/       # Audit, evidence, and deterministic/Gemini LLM services
    knowledge/          # Seeded synthetic compliance policy JSON documents
    samples/            # Sample clean, exception, and hold case JSON payloads
    scripts/            # Setup, run, and automated smoke test scripts
    tests/              # Pytest test suite
```
