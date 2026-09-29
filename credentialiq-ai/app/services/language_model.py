"""Language Model Service with optional Gemini API integration and deterministic fallback."""

import json

from app.core.config import settings
from app.core.enums import RiskLevel
from app.core.logging import logger
from app.core.security import PIISanitizer
from app.schemas.common import LicenseEvidenceResult, PolicyChunkMatch, SanctionEvidenceResult
from app.schemas.responses import RiskAssessmentResponse
from app.services.deterministic_language_model import DeterministicLanguageModelService


class LanguageModelService:
    """Orchestrates risk assessment via official Gemini API or deterministic fallback engine."""

    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.deterministic_engine = DeterministicLanguageModelService()

    def evaluate_risk(
        self,
        provider_data: dict,
        licenses: list[LicenseEvidenceResult],
        sanctions: list[SanctionEvidenceResult],
        policies: list[PolicyChunkMatch],
    ) -> RiskAssessmentResponse:
        """Perform risk evaluation using Gemini if configured, or deterministic fallback."""
        if self.provider.lower() == "gemini" and settings.GEMINI_API_KEY:
            try:
                return self._evaluate_with_gemini(provider_data, licenses, sanctions, policies)
            except Exception as e:
                logger.warning(
                    f"Gemini API evaluation failed or timed out ({e}). Falling back to deterministic model."
                )
                return self.deterministic_engine.evaluate_risk(
                    provider_data, licenses, sanctions, policies
                )

        logger.info("Using deterministic risk assessment engine.")
        return self.deterministic_engine.evaluate_risk(
            provider_data, licenses, sanctions, policies
        )

    def _evaluate_with_gemini(
        self,
        provider_data: dict,
        licenses: list[LicenseEvidenceResult],
        sanctions: list[SanctionEvidenceResult],
        policies: list[PolicyChunkMatch],
    ) -> RiskAssessmentResponse:
        """Call official google-genai SDK for risk evaluation."""
        from google import genai
        from google.genai import types

        sanitized_provider = PIISanitizer.sanitize_provider_data(provider_data)

        prompt = f"""
You are a senior healthcare compliance AI risk assessor for CredentialIQ.
Analyze the following provider credentialing case and evaluate risk:

PROVIDER DATA (Sanitized):
{json.dumps(sanitized_provider, indent=2)}

PRIMARY SOURCE LICENSES:
{[lic_item.model_dump() for lic_item in licenses]}

SANCTION & EXCLUSION SCREENINGS:
{[s.model_dump() for s in sanctions]}

APPLICABLE POLICY RULES:
{[p.model_dump() for p in policies]}

SAFETY CONSTRAINTS:
1. If any license is SUSPENDED or REVOKED, or any sanction MATCH_FOUND, Risk Level MUST BE 'Hold' and score MUST BE >= 90.0.
2. If any license is EXPIRED or has disciplinary actions, Risk Level MUST BE 'Exception' and score between 40.0 and 60.0.
3. If all clean, Risk Level MUST BE 'Clean' and score < 15.0.

Respond strictly in JSON format with fields:
- "risk_level": "Clean" | "Exception" | "Hold"
- "score": float between 0.0 and 100.0
- "summary": string
- "risk_factors": list of strings
- "mitigating_factors": list of strings
"""

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        response_text = response.text
        if not response_text:
            raise ValueError("Empty response from Gemini model.")

        parsed = json.loads(response_text)

        raw_risk_level = parsed.get("risk_level", "Clean")
        risk_level = RiskLevel(raw_risk_level)

        # Enforce safety guardrail on LLM output
        has_critical = any(
            lic_item.status.value in ["Suspended", "Revoked"] for lic_item in licenses
        ) or any(s.match_found for s in sanctions)
        if has_critical and risk_level != RiskLevel.HOLD:
            logger.warning("Gemini output violated critical safety guardrail. Overriding to HOLD.")
            risk_level = RiskLevel.HOLD
            parsed["score"] = 95.0

        return RiskAssessmentResponse(
            risk_level=risk_level,
            score=float(parsed.get("score", 50.0)),
            summary=parsed.get("summary", "Risk evaluation completed."),
            risk_factors=parsed.get("risk_factors", []),
            mitigating_factors=parsed.get("mitigating_factors", []),
            applicable_policies=policies,
        )
