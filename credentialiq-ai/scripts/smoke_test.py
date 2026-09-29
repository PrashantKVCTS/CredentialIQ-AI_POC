#!/usr/bin/env python3
"""Automated API Smoke Test for CredentialIQ AI POC."""

import json
import sys
import time
from pathlib import Path
import httpx

BASE_URL = "http://127.0.0.1:8000"
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def run_smoke_tests():
    """Execute end-to-end API smoke test suite."""
    print("==================================================")
    print(" Starting CredentialIQ AI API Smoke Tests")
    print("==================================================")

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Health Checks
    print("\n[1/8] Testing Health Endpoints...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"  ✓ /health: {res.json()['status']}")

    res = client.get("/health/ready")
    assert res.status_code == 200, f"Readiness check failed: {res.text}"
    print(f"  ✓ /health/ready: {res.json()['status']}")

    # 2. System Info & RAG Search
    print("\n[2/8] Testing System Info & Policy RAG Search...")
    res = client.get("/api/v1/system/info")
    assert res.status_code == 200
    print(f"  ✓ System Provider: {res.json()['llm_provider']}")

    res = client.get("/api/v1/system/rag/search", params={"q": "NCQA license verification"})
    assert res.status_code == 200
    rag_data = res.json()
    assert rag_data["total_matches"] > 0, "RAG search returned 0 matches"
    print(f"  ✓ Policy RAG Search: Found {rag_data['total_matches']} policy matches")

    # 3. Process Clean Provider Case
    print("\n[3/8] Processing Clean Provider Case...")
    clean_payload = json.loads((SAMPLES_DIR / "clean_provider_case.json").read_text())
    res = client.post("/api/v1/cases/process", json=clean_payload)
    assert res.status_code == 201, f"Clean case processing failed: {res.text}"
    clean_case = res.json()
    assert clean_case["status"] == "Clean", f"Expected Clean status, got {clean_case['status']}"
    assert (
        clean_case["workflow_recommendation"]["recommendation"] == "AutoApprove"
    ), f"Expected AutoApprove, got {clean_case['workflow_recommendation']['recommendation']}"
    clean_id = clean_case["case_id"]
    print(f"  ✓ Clean Case processed successfully (ID: {clean_id[:8]}..., Decision: AutoApprove)")

    # 4. Process Exception Provider Case
    print("\n[4/8] Processing Exception Provider Case...")
    exp_payload = json.loads((SAMPLES_DIR / "exception_provider_case.json").read_text())
    res = client.post("/api/v1/cases/process", json=exp_payload)
    assert res.status_code == 201
    exp_case = res.json()
    assert exp_case["status"] == "Exception"
    assert exp_case["workflow_recommendation"]["recommendation"] == "CommitteeReview"
    exp_id = exp_case["case_id"]
    print(f"  ✓ Exception Case processed successfully (ID: {exp_id[:8]}..., Decision: CommitteeReview)")

    # 5. Process Hold Provider Case
    print("\n[5/8] Processing Hold Provider Case...")
    hold_payload = json.loads((SAMPLES_DIR / "hold_provider_case.json").read_text())
    res = client.post("/api/v1/cases/process", json=hold_payload)
    assert res.status_code == 201
    hold_case = res.json()
    assert hold_case["status"] == "Hold"
    assert hold_case["workflow_recommendation"]["recommendation"] == "Deny"
    hold_id = hold_case["case_id"]
    print(f"  ✓ Hold Case processed successfully (ID: {hold_id[:8]}..., Decision: Deny)")

    # 6. Test Human Reviewer Override
    print("\n[6/8] Testing Human Reviewer Override Endpoint...")
    override_payload = {
        "reviewer_id": "DrSmith_Chair",
        "override_decision": "Approved",
        "rationale": "Overriding exception based on additional verified continuing education credits.",
    }
    res = client.post(f"/api/v1/cases/{exp_id}/override", json=override_payload)
    assert res.status_code == 200, f"Override failed: {res.text}"
    overridden_case = res.json()
    assert overridden_case["status"] == "Overridden"
    print(f"  ✓ Human Override applied successfully to case {exp_id[:8]}...")

    # 7. Test Audit Trail
    print("\n[7/8] Testing Case Audit Trail Retrieval...")
    res = client.get(f"/api/v1/cases/{clean_id}/audit-trail")
    assert res.status_code == 200
    audit_events = res.json()
    assert len(audit_events) >= 5, f"Expected at least 5 audit events, got {len(audit_events)}"
    print(f"  ✓ Retrieved {len(audit_events)} audit events for clean case.")

    # 8. Test Case List
    print("\n[8/8] Testing Case Listing Endpoint...")
    res = client.get("/api/v1/cases")
    assert res.status_code == 200
    cases_list = res.json()
    assert len(cases_list) >= 3
    print(f"  ✓ Case listing returned {len(cases_list)} cases.")

    print("\n==================================================")
    print(" ALL API SMOKE TESTS PASSED SUCCESSFULLY! (100%)")
    print("==================================================")


if __name__ == "__main__":
    try:
        run_smoke_tests()
    except Exception as err:
        print(f"\n❌ SMOKE TEST FAILED: {err}", file=sys.stderr)
        sys.exit(1)
