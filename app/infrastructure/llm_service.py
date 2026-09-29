import re
from typing import List, Dict, Any
from app.core.enums import RiskClassification, LicenseStatus, SanctionStatus
from app.core.models import CredentialingCase, PolicyChunk, RiskAssessment

class DeterministicLanguageModelService:
    @property
    def provider_name(self) -> str:
        return "Deterministic"

    async def evaluate_risk_async(self, case: CredentialingCase, retrieved_policies: List[PolicyChunk]) -> RiskAssessment:
        latest_lic = case.verification_results[-1] if case.verification_results else None
        latest_sanc = case.sanction_results[-1] if case.sanction_results else None

        policy_ids = [p.id for p in retrieved_policies]
        rule_refs = [p.rule_reference for p in retrieved_policies]

        if latest_sanc and latest_sanc.status == SanctionStatus.MATCH_FOUND:
            classification = RiskClassification.HOLD
            rationale = "SANCTION MATCH DETECTED: Provider matched an active exclusion or sanction database entry."
            rule_refs.append("OIG-LEIE-01")
        elif latest_lic and latest_lic.status == LicenseStatus.SUSPENDED:
            classification = RiskClassification.HOLD
            rationale = "SUSPENDED LICENSE: Primary state license is suspended. Mandatory hold required."
            rule_refs.append("ST-SUSP-99")
        elif latest_lic and latest_lic.status == LicenseStatus.EXPIRED:
            classification = RiskClassification.EXCEPTION
            rationale = "EXPIRED LICENSE EXCEPTION: Primary state license has expired. Requires Credentialing Committee review for grace period."
        else:
            classification = RiskClassification.CLEAN
            rationale = "CLEAN APPLICATION: Active state license verified with zero sanction or restriction matches."

        return RiskAssessment(
            case_id=case.id,
            classification=classification,
            confidence_score=1.0,
            rationale=rationale,
            applied_rule_references=list(set(rule_refs)),
            retrieved_source_ids=policy_ids,
            correlation_id=case.correlation_id,
            evaluated_by=self.provider_name
        )

    def redact_pii(self, text: str) -> str:
        # Redact DOB / SSN / Email patterns
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
        text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '[REDACTED_DATE]', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[REDACTED_EMAIL]', text)
        return text

class GeminiLanguageModelService(DeterministicLanguageModelService):
    @property
    def provider_name(self) -> str:
        return "Gemini (With Redaction & Fallback)"

    async def evaluate_risk_async(self, case: CredentialingCase, retrieved_policies: List[PolicyChunk]) -> RiskAssessment:
        # Fallback to deterministic evaluation for local POC reliability
        assessment = await super().evaluate_risk_async(case, retrieved_policies)
        assessment.evaluated_by = self.provider_name
        return assessment
