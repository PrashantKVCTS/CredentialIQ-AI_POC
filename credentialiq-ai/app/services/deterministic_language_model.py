"""Deterministic language model service evaluating provider risk using rule-based algorithms."""

from app.core.enums import LicenseStatus, RiskLevel, SanctionStatus
from app.schemas.common import LicenseEvidenceResult, PolicyChunkMatch, SanctionEvidenceResult
from app.schemas.responses import RiskAssessmentResponse


class DeterministicLanguageModelService:
    """Rule-based risk assessment service providing deterministic evaluations without cloud LLMs."""

    def evaluate_risk(
        self,
        provider_data: dict,
        licenses: list[LicenseEvidenceResult],
        sanctions: list[SanctionEvidenceResult],
        policies: list[PolicyChunkMatch],
    ) -> RiskAssessmentResponse:
        """Evaluate provider risk deterministically enforcing strict compliance safety rules."""
        risk_factors: list[str] = []
        mitigating_factors: list[str] = []

        # 1. Check Sanctions (Critical Hold Constraint)
        has_sanction = False
        for s in sanctions:
            if s.match_found or s.status == SanctionStatus.MATCH_FOUND:
                has_sanction = True
                risk_factors.append(
                    f"CRITICAL SANCTION MATCH: Found active record in {s.database_name} - {s.details or s.exclusion_type}"
                )

        # 2. Check License Statuses (Critical Hold vs Exception)
        has_suspended_or_revoked = False
        has_expired_or_disciplinary = False

        for lic in licenses:
            if lic.status in [LicenseStatus.SUSPENDED, LicenseStatus.REVOKED]:
                has_suspended_or_revoked = True
                risk_factors.append(
                    f"CRITICAL LICENSE ENCUMBRANCE: License {lic.license_number} ({lic.state}) is {lic.status.value}."
                )
            elif lic.status == LicenseStatus.EXPIRED:
                has_expired_or_disciplinary = True
                risk_factors.append(
                    f"LICENSE EXPIRED: License {lic.license_number} ({lic.state}) has status EXPIRED."
                )

            if lic.has_disciplinary_action:
                has_expired_or_disciplinary = True
                risk_factors.append(
                    f"DISCIPLINARY ACTION RECORDED: Board record for {lic.license_number} ({lic.state}) - {lic.disciplinary_details}"
                )

        # 3. Check Education & Board Certification
        if provider_data.get("board_certified"):
            mitigating_factors.append("Provider maintains active board certification.")
        else:
            risk_factors.append("Provider is not board certified in reported specialty.")

        # Determine Final Risk Level
        if has_sanction or has_suspended_or_revoked:
            risk_level = RiskLevel.HOLD
            score = 95.0
            summary = (
                "HOLD - Critical compliance violation detected. Active federal sanctions or "
                "state license encumbrances prevent credentialing approval."
            )
        elif has_expired_or_disciplinary:
            risk_level = RiskLevel.EXCEPTION
            score = 48.0
            summary = (
                "EXCEPTION - Credentialing exceptions identified (expired license or past board "
                "disciplinary inquiry). Credentialing Committee review required."
            )
        else:
            risk_level = RiskLevel.CLEAN
            score = 5.0
            mitigating_factors.append("All state licenses are active and unencumbered.")
            mitigating_factors.append("Zero sanction or exclusion matches found across federal databases.")
            summary = (
                "CLEAN - All primary source verifications and sanction screenings are clear "
                "and fully compliant with NCQA and payer policies."
            )

        return RiskAssessmentResponse(
            risk_level=risk_level,
            score=score,
            summary=summary,
            risk_factors=risk_factors,
            mitigating_factors=mitigating_factors,
            applicable_policies=policies,
        )
