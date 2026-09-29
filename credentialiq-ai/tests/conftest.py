"""Pytest fixtures for CredentialIQ AI test suite."""

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.main import app
from app.models.database import Base


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Create a fresh in-memory SQLite database session with StaticPool for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        json_serializer=lambda obj: json.dumps(obj, default=str),
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """FastAPI TestClient with overridden database session dependency."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_clean_provider() -> dict:
    """Sample clean provider intake payload."""
    return {
        "npi": "1234567890",
        "first_name": "Eleanor",
        "last_name": "Vance",
        "date_of_birth": "1980-05-14",
        "ssn": "999-00-1234",
        "taxonomy_code": "207Q00000X",
        "specialty": "Family Medicine",
        "medical_school": "Stanford University School of Medicine",
        "graduation_year": 2006,
        "board_certified": True,
        "board_name": "American Board of Family Medicine",
        "licenses": [
            {
                "license_number": "C123456",
                "state": "CA",
                "license_type": "MD",
                "expiration_date": "2027-12-31",
            }
        ],
    }


@pytest.fixture
def sample_hold_provider() -> dict:
    """Sample hold provider intake payload with active suspension."""
    return {
        "npi": "3333333333",
        "first_name": "Victor",
        "last_name": "VonDoom",
        "date_of_birth": "1968-03-01",
        "ssn": "999-00-9999",
        "taxonomy_code": "208600000X",
        "specialty": "Surgery",
        "medical_school": "State University Medical Center",
        "graduation_year": 1994,
        "board_certified": True,
        "board_name": "American Board of Surgery",
        "licenses": [
            {
                "license_number": "FL33333",
                "state": "FL",
                "license_type": "MD",
                "expiration_date": "2025-05-20",
            }
        ],
    }
