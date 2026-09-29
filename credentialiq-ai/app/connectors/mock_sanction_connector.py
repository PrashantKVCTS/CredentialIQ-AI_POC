"""Mock sanction connector simulating OIG LEIE, SAM.gov, and NPDB screening."""

from datetime import datetime
from typing import Any

from app.connectors.interfaces import ISanctionConnector
from app.core.enums import SanctionStatus
from app.schemas.common import EvidenceMetadata, SanctionEvidenceResult


class MockSanctionConnector(ISanctionConnector):
    """Simulates federal and state sanction screening."""

    # Synthetic sanction records by NPI
    MOCK_SANCTIONS: dict[str, list[dict[str, Any]]] = {
        # Hold provider (Sanction match)
        "3333333333": [
            {
                "database_name": "OIG_LEIE",
                "status": SanctionStatus.MATCH_FOUND,
                "match_found": True,
                "exclusion_type": "1128(a)(1) - Mandatory Exclusion",
                "reinstatement_date": None,
                "details": "Active exclusion from participating in Federal healthcare programs.",
            },
            {
                "database_name": "SAM_GOV",
                "status": SanctionStatus.MATCH_FOUND,
                "match_found": True,
                "exclusion_type": "Debarment",
                "reinstatement_date": None,
                "details": "Active federal contract debarment.",
            },
            {
                "database_name": "NPDB",
                "status": SanctionStatus.MATCH_FOUND,
                "match_found": True,
                "exclusion_type": "Adverse Action Report",
                "reinstatement_date": None,
                "details": "Emergency suspension reported by State Board.",
            },
        ],
    }

    def screen_sanctions(
        self, provider_npi: str, first_name: str, last_name: str
    ) -> list[SanctionEvidenceResult]:
        """Screen provider against federal exclusion databases."""
        if provider_npi in self.MOCK_SANCTIONS:
            records = self.MOCK_SANCTIONS[provider_npi]
            results = []
            for r in records:
                sanc_status: SanctionStatus = r["status"]
                results.append(
                    SanctionEvidenceResult(
                        database_name=str(r["database_name"]),
                        status=sanc_status,
                        match_found=bool(r["match_found"]),
                        exclusion_type=r["exclusion_type"],
                        reinstatement_date=r["reinstatement_date"],
                        details=r["details"],
                        metadata=EvidenceMetadata(
                            source_system=f"{r['database_name']}_MockDatabase",
                            verified_at_utc=datetime.utcnow(),
                            is_simulated=True,
                            confidence_score=0.98,
                            raw_response_snippet=f"Matched record in {r['database_name']} for NPI {provider_npi}: {r['details']}",
                        ),
                    )
                )
            return results

        # Clean screening default for unflagged NPIs
        databases = ["OIG_LEIE", "SAM_GOV", "NPDB"]
        results = []
        for db_name in databases:
            results.append(
                SanctionEvidenceResult(
                    database_name=db_name,
                    status=SanctionStatus.CLEAR,
                    match_found=False,
                    exclusion_type=None,
                    reinstatement_date=None,
                    details="No exclusion or sanction records found.",
                    metadata=EvidenceMetadata(
                        source_system=f"{db_name}_MockDatabase",
                        verified_at_utc=datetime.utcnow(),
                        is_simulated=True,
                        confidence_score=1.0,
                        raw_response_snippet=f"0 results returned from {db_name} query for NPI {provider_npi}.",
                    ),
                )
            )

        return results
