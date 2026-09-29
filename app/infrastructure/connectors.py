import uuid
from datetime import datetime, timezone, timedelta
from app.core.enums import LicenseStatus, SanctionStatus
from app.core.models import Provider, VerificationResult, SanctionCheckResult

class MockStateBoardConnector:
    async def verify_license_async(self, provider: Provider, correlation_id: str) -> VerificationResult:
        license_num = provider.license_number.upper()
        now = datetime.now(timezone.utc)
        
        if "EXP" in license_num:
            status = LicenseStatus.EXPIRED
            exp_date = now - timedelta(days=60)
            explanation = f"[SIMULATED] License {provider.license_number} in state {provider.primary_state} expired on {exp_date.strftime('%Y-%m-%d')}."
        elif "SUSP" in license_num or "REV" in license_num:
            status = LicenseStatus.SUSPENDED
            exp_date = now + timedelta(days=365)
            explanation = f"[SIMULATED] License {provider.license_number} in state {provider.primary_state} is SUSPENDED due to board disciplinary action."
        else:
            status = LicenseStatus.ACTIVE
            exp_date = now + timedelta(days=365)
            explanation = f"[SIMULATED] License {provider.license_number} verified Active and in good standing with {provider.primary_state} State Licensing Board."

        return VerificationResult(
            source="MockStateMedicalBoardConnector",
            status=status,
            expiration_date=exp_date,
            verified_at_utc=now,
            correlation_id=correlation_id,
            evidence_reference=f"SIM-DOC-STATEBOARD-{uuid.uuid4().hex}",
            is_simulated=True,
            human_readable_explanation=explanation
        )

class MockSanctionConnector:
    async def check_sanctions_async(self, provider: Provider, correlation_id: str) -> SanctionCheckResult:
        name = f"{provider.first_name} {provider.last_name}".upper()
        license_num = provider.license_number.upper()
        now = datetime.now(timezone.utc)

        if "SANCTION" in name or "EXCLUDE" in name or "SUSP" in license_num:
            status = SanctionStatus.MATCH_FOUND
            explanation = f"[SIMULATED] MATCH FOUND: Provider {provider.first_name} {provider.last_name} (NPI: {provider.npi}) matched an active exclusion entry on OIG LEIE / SAM.gov."
        else:
            status = SanctionStatus.CLEAR
            explanation = f"[SIMULATED] CLEAR: Provider NPI {provider.npi} ({provider.first_name} {provider.last_name}) searched across OIG LEIE, SAM.gov, and NPDB database. No exclusions or sanctions found."

        return SanctionCheckResult(
            source="MockSanctionScreeningConnector (OIG/SAM/NPDB)",
            status=status,
            verified_at_utc=now,
            correlation_id=correlation_id,
            evidence_reference=f"SIM-DOC-SANCTION-{uuid.uuid4().hex}",
            is_simulated=True,
            human_readable_explanation=explanation
        )
