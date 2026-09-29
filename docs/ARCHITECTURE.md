# CredentialIQ AI - Architecture Documentation

## System Component Architecture

```mermaid
graph TD
    Client[HTTP Client / Swagger UI / CLI] -->|REST API Requests| API[CredentialIQ.Api Layer]
    API -->|DI & Services| Orchestrator[CredentialingOrchestrator]
    
    subgraph Agent Pipeline (Sequential Flow)
        Agent1[1. CredentialVerificationAgent] --> Agent2[2. LicenseVerificationAgent]
        Agent2 --> Agent3[3. SanctionCheckAgent]
        Agent3 --> Agent4[4. RiskAssessmentAgent]
        Agent4 --> Agent5[5. WorkflowAgent]
    end

    Orchestrator -->|Passes CredentialingCase| Agent1
    
    Agent2 -->|Primary Source Mock| LicConnector[IVerificationConnector / MockStateBoard]
    Agent3 -->|Screening Mock| SancConnector[ISanctionConnector / MockSanction]
    Agent4 -->|Local RAG Search| RAGRepo[IRagRepository / LocalRagRepository]
    Agent4 -->|LLM Risk Analysis| LLM[ILanguageModelService / Deterministic or Gemini]
    
    RAGRepo -->|Seeded Synthetic Rules| PolicyStore[(knowledge/ directory JSON)]
    Orchestrator -->|EF Core Persistence| DB[(SQLite: credentialiq.db)]
```

---

## Agent Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Controller as CredentialingCasesController
    participant Orch as CredentialingOrchestrator
    participant ValAgent as CredentialVerificationAgent
    participant LicAgent as LicenseVerificationAgent
    participant SancAgent as SanctionCheckAgent
    participant RiskAgent as RiskAssessmentAgent
    participant WfAgent as WorkflowAgent
    participant DB as SQLite DB

    Client->>Controller: POST /api/credentialingcases (Provider Intake)
    Controller->>DB: Save initial Intake case
    Controller->>Orch: ProcessCaseAsync(case)
    
    Orch->>ValAgent: ExecuteAsync(case)
    ValAgent-->>Orch: Validated & Normalized Case

    Orch->>LicAgent: ExecuteAsync(case)
    LicAgent-->>Orch: License Verification Result Appended

    Orch->>SancAgent: ExecuteAsync(case)
    SancAgent-->>Orch: Sanction Screening Result Appended

    Orch->>RiskAgent: ExecuteAsync(case)
    RiskAgent-->>Orch: Grounded Risk Assessment Appended

    Orch->>WfAgent: ExecuteAsync(case)
    WfAgent-->>Orch: Final Recommendation Appended (Approved / CommitteeReview / OnHold)

    Orch-->>Controller: Completed CredentialingCase
    Controller->>DB: Save complete case & evidence audit log
    Controller-->>Client: 201 Created (CredentialingCaseResponse)
```

---

## Local Development vs. Production Architecture

| Component | Local Proof-of-Concept Profile | Future Production Target Profile |
| :--- | :--- | :--- |
| **Database** | Entity Framework Core + SQLite | Azure SQL / PostgreSQL with Geo-Replication |
| **RAG Policy Engine** | `LocalRagRepository` (Keyword + TF Scoring) | Azure AI Search (Vector Hybrid Search + Azure OpenAI Embeddings) |
| **LLM Provider** | `DeterministicLanguageModelService` (or Gemini API) | Azure OpenAI / Gemini Enterprise Enterprise Tenant |
| **Primary Source Verification** | `MockStateBoardConnector` | Direct State Medical Board API Connectors / CAQH ProView API |
| **Sanction Screening** | `MockSanctionConnector` | Real-time OIG LEIE, SAM.gov, and NPDB Query Gateway |
