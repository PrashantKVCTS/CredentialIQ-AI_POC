"""Connector interfaces for primary-source verification."""

from abc import ABC, abstractmethod

from app.schemas.common import LicenseEvidenceResult, SanctionEvidenceResult


class ILicenseConnector(ABC):
    """Interface for state medical board primary source license verification."""

    @abstractmethod
    def verify_license(
        self, license_number: str, state: str, provider_npi: str
    ) -> LicenseEvidenceResult:
        """Verify license status against state board database."""
        pass


class ISanctionConnector(ABC):
    """Interface for federal/state sanction database screening (OIG, SAM, NPDB)."""

    @abstractmethod
    def screen_sanctions(
        self, provider_npi: str, first_name: str, last_name: str
    ) -> list[SanctionEvidenceResult]:
        """Screen provider against exclusion and sanction databases."""
        pass
