# CredentialIQ AI - Security Policy & Considerations

## 1. Synthetic Data Default & Non-Production Notice
- All default provider data, license numbers, and sanction records in this POC are **100% fictional**.
- The system explicitly marks all mock outputs with `IsSimulated = true`.
- Real healthcare provider PII must **never** be entered into this demonstration instance.

## 2. PII Redaction & Minimization
- Before prompts are sent to external LLMs (such as Gemini), sensitive provider fields (DOB, SSN, Tax ID, personal home address) are automatically redacted by `GeminiLanguageModelService`.
- Only minimal required fields (Provider Type, State, License Verification Status, Sanction Status) are passed for policy risk assessment.

## 3. Secret Management
- API Keys, connection strings, and tokens must never be hardcoded or checked into source control.
- Secret resolution order:
  1. Environment Variables (`GEMINI_API_KEY`)
  2. .NET User Secrets (`dotnet user-secrets set "Gemini:ApiKey" "..."`)
  3. `.env` file (excluded via `.gitignore`)

## 4. Prompt Injection Mitigation
- LLM prompt templates treat policy chunks and provider findings as untrusted input blocks wrapped in explicit demarcation fences.
- All LLM responses are parsed strictly as structured JSON schemas; missing or malformed fields trigger immediate fallback to `DeterministicLanguageModelService`.

## 5. Human-in-the-Loop Safeguards
- Suspended licenses and sanction matches are hard-coded to **never auto-approve**.
- All API outputs prominently feature a legal disclaimer: *CredentialIQ AI recommendations are simulated for demonstration purposes only and require review and authorization by an authorized human credentialing committee.*
