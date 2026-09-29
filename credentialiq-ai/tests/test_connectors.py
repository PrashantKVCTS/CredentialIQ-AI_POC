"""Unit tests for mock license and sanction connectors."""

from app.connectors.mock_license_connector import MockLicenseConnector
from app.connectors.mock_sanction_connector import MockSanctionConnector
from app.core.enums import LicenseStatus, SanctionStatus


def test_mock_license_connector_clean():
    connector = MockLicenseConnector()
    res = connector.verify_license("C123456", "CA", "1234567890")

    assert res.license_number == "C123456"
    assert res.state == "CA"
    assert res.status == LicenseStatus.ACTIVE
    assert not res.has_disciplinary_action
    assert res.metadata.is_simulated is True
    assert "StateBoard_CA" in res.metadata.source_system


def test_mock_license_connector_suspended():
    connector = MockLicenseConnector()
    res = connector.verify_license("FL33333", "FL", "3333333333")

    assert res.status == LicenseStatus.SUSPENDED
    assert res.has_disciplinary_action is True
    assert res.metadata.is_simulated is True


def test_mock_sanction_connector_clear():
    connector = MockSanctionConnector()
    results = connector.screen_sanctions("1234567890", "Eleanor", "Vance")

    assert len(results) == 3
    assert all(r.status == SanctionStatus.CLEAR for r in results)
    assert all(r.match_found is False for r in results)
    assert all(r.metadata.is_simulated is True for r in results)


def test_mock_sanction_connector_match():
    connector = MockSanctionConnector()
    results = connector.screen_sanctions("3333333333", "Victor", "VonDoom")

    assert len(results) == 3
    assert any(r.match_found is True for r in results)
    oig_match = next(r for r in results if r.database_name == "OIG_LEIE")
    assert oig_match.status == SanctionStatus.MATCH_FOUND
    assert oig_match.exclusion_type is not None
