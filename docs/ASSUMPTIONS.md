# CredentialIQ AI - Technical Assumptions & Design Boundaries

## Key Assumptions

1. **Local Offline Execution**:
   - The application is assumed to run completely locally without requiring active Azure subscriptions, cloud databases, or live regulatory web scraping.
2. **Deterministic Fallback Default**:
   - In environments where no Gemini API key is configured or where network access is restricted, the application relies on `DeterministicLanguageModelService` to ensure deterministic, reproducible test runs.
3. **Mock Primary Source Verification**:
   - State Medical Boards, OIG LEIE, SAM.gov, and NPDB connectors are mocked deterministically based on synthetic license numbers (`EXP-`, `SUSP-`, `NF-`) and NPI suffixes (`999`).
4. **Local Vector-Like RAG Policy Repository**:
   - Policy documents stored in `knowledge/` are formatted as JSON policy chunks with metadata attributes (`SourceType`, `Jurisdiction`, `ProviderType`, `RuleReference`). Term frequency matching combined with metadata filtering simulates vector search behavior for local proof-of-concept demonstration.
5. **Human Override Preservation**:
   - When a human reviewer overrides an automated workflow decision via `POST /api/credentialingcases/{id}/override`, the original agent recommendation remains permanently recorded in the immutable audit trail.
