"""Evidence service managing primary-source evidence compilation."""

from app.connectors.interfaces import ILicenseConnector, ISanctionConnector
from app.connectors.mock_license_connector import MockLicenseConnector
from app.connectors.mock_sanction_connector import MockSanctionConnector
from app.schemas.common import LicenseEvidenceResult, SanctionEvidenceResult


class EvidenceService:
    """Service to gather primary source evidence from state boards and sanction databases."""

    def __init__(
        self,
        license_connector: ILicenseConnector | None = None,
        sanction_connector: ISanctionConnector | None = None,
    ):
        self.license_connector = license_connector or MockLicenseConnector()
        self.sanction_connector = sanction_connector or MockSanctionConnector()

    def verify_licenses(
        self, licenses: list[dict], provider_npi: str
    ) -> list[LicenseEvidenceResult]:
        """Verify list of state licenses against primary sources."""
        results = []
        for lic in licenses:
            lic_num = lic.get("license_number", "")
            state = lic.get("state", "")
            res = self.license_connector.verify_license(lic_num, state, provider_npi)
            results.append(res)
        return results

    def screen_sanctions(
        self, provider_npi: str, first_name: str, last_name: str
    ) -> list[SanctionEvidenceResult]:
        """Screen provider across sanction databases."""
        return self.sanction_connector.screen_sanctions(provider_npi, first_name, last_name)
