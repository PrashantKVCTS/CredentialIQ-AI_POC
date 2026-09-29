"""Mock primary-source license connector simulating State Medical Boards."""

from datetime import datetime
from typing import Any

from app.connectors.interfaces import ILicenseConnector
from app.core.enums import LicenseStatus
from app.schemas.common import EvidenceMetadata, LicenseEvidenceResult


class MockLicenseConnector(ILicenseConnector):
    """Simulates primary source state medical board queries using synthetic dataset."""

    # Synthetic license database
    MOCK_LICENSES: dict[tuple[str, str], dict[str, Any]] = {
        # Clean providers
        ("1234567890", "CA"): {
            "license_number": "C123456",
            "state": "CA",
            "status": LicenseStatus.ACTIVE,
            "expiration_date": "2027-12-31",
            "has_disciplinary_action": False,
            "disciplinary_details": None,
        },
        ("1234567890", "NY"): {
            "license_number": "NY987654",
            "state": "NY",
            "status": LicenseStatus.ACTIVE,
            "expiration_date": "2026-10-31",
            "has_disciplinary_action": False,
            "disciplinary_details": None,
        },
        # Exception provider (expired or past minor disciplinary action)
        ("2222222222", "CA"): {
            "license_number": "CA22222",
            "state": "CA",
            "status": LicenseStatus.ACTIVE,
            "expiration_date": "2025-08-15",
            "has_disciplinary_action": True,
            "disciplinary_details": "2021 Administrative warning for delayed chart sign-off. Remedied.",
        },
        ("2222222222", "TX"): {
            "license_number": "TX55555",
            "state": "TX",
            "status": LicenseStatus.EXPIRED,
            "expiration_date": "2023-01-01",
            "has_disciplinary_action": False,
            "disciplinary_details": "License expired due to non-renewal upon moving practice state.",
        },
        # Hold provider (suspended / revoked)
        ("3333333333", "FL"): {
            "license_number": "FL33333",
            "state": "FL",
            "status": LicenseStatus.SUSPENDED,
            "expiration_date": "2025-05-20",
            "has_disciplinary_action": True,
            "disciplinary_details": "Active emergency suspension order issued by FL Medical Board.",
        },
    }

    def verify_license(
        self, license_number: str, state: str, provider_npi: str
    ) -> LicenseEvidenceResult:
        """Query mock state board database."""
        key = (provider_npi, state.upper())
        rec: dict[str, Any] | None = self.MOCK_LICENSES.get(key)

        # Fallback for arbitrary license inputs
        if not rec:
            if "SUSPEND" in license_number.upper():
                status = LicenseStatus.SUSPENDED
                has_disc = True
                disc: str | None = "Simulated active suspension"
            elif "EXP" in license_number.upper():
                status = LicenseStatus.EXPIRED
                has_disc = False
                disc = "Simulated expired license"
            else:
                status = LicenseStatus.ACTIVE
                has_disc = False
                disc = None

            rec = {
                "license_number": license_number,
                "state": state.upper(),
                "status": status,
                "expiration_date": "2027-01-01",
                "has_disciplinary_action": has_disc,
                "disciplinary_details": disc,
            }

        lic_status: LicenseStatus = rec["status"]

        return LicenseEvidenceResult(
            license_number=str(rec["license_number"]),
            state=str(rec["state"]),
            status=lic_status,
            expiration_date=rec["expiration_date"],
            has_disciplinary_action=bool(rec["has_disciplinary_action"]),
            disciplinary_details=rec["disciplinary_details"],
            metadata=EvidenceMetadata(
                source_system=f"StateBoard_{state.upper()}_PrimarySourceMock",
                verified_at_utc=datetime.utcnow(),
                is_simulated=True,
                confidence_score=1.0,
                raw_response_snippet=f"Primary source query result for License {license_number} ({state}): Status={rec['status']}",
            ),
        )
