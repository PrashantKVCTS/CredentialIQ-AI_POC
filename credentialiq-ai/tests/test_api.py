"""Integration tests for REST API routes."""


def test_health_endpoints(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res = client.get("/health/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"


def test_system_info_and_rag(client):
    res = client.get("/api/v1/system/info")
    assert res.status_code == 200

    res = client.get("/api/v1/system/rag/search", params={"q": "NCQA license"})
    assert res.status_code == 200
    assert res.json()["total_matches"] > 0


def test_process_case_and_override(client, sample_clean_provider):
    # Process case
    res = client.post("/api/v1/cases/process", json={"provider": sample_clean_provider})
    assert res.status_code == 201
    data = res.json()
    case_id = data["case_id"]
    assert data["status"] == "Clean"

    # Get case details
    res = client.get(f"/api/v1/cases/{case_id}")
    assert res.status_code == 200
    assert res.json()["case_id"] == case_id

    # List cases
    res = client.get("/api/v1/cases")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Apply override
    override_payload = {
        "reviewer_id": "DrAdmin",
        "override_decision": "Approved",
        "rationale": "Special approval granted.",
    }
    res = client.post(f"/api/v1/cases/{case_id}/override", json=override_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "Overridden"

    # Fetch audit trail
    res = client.get(f"/api/v1/cases/{case_id}/audit-trail")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 5
    assert any(e["event_type"] == "HumanOverride" for e in events)
