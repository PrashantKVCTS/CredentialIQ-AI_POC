# CredentialIQ AI - API Testing Guide

## Base URL
Default local endpoint: `http://localhost:5050`

## Endpoints Summary

### 1. Intake and Process Credentialing Case
- **Method**: `POST`
- **Path**: `/api/credentialingcases`
- **Request Body**:
```json
{
  "npi": "1234567890",
  "firstName": "Jane",
  "lastName": "Doe",
  "providerType": "Medical Doctor",
  "primaryState": "CA",
  "licenseNumber": "C12345",
  "dateOfBirth": "1980-05-15T00:00:00Z",
  "email": "dr.jane.doe@example.org"
}
```
- **Response**: `201 Created` with full case status and evidence pointers.

---

### 2. Get Case by ID
- **Method**: `GET`
- **Path**: `/api/credentialingcases/{id}`
- **Response**: `200 OK` with stored case details.

---

### 3. Get Structured Evidence & Audit Trail
- **Method**: `GET`
- **Path**: `/api/credentialingcases/{id}/evidence`
- **Response**: `200 OK` with complete evidence breakdown, timestamped audit events, and simulation tags.

---

### 4. Submit Manual Reviewer Override
- **Method**: `POST`
- **Path**: `/api/credentialingcases/{id}/override`
- **Request Body**:
```json
{
  "targetStatus": "Approved",
  "reviewerName": "Dr. Alice Vance (Credentialing Committee Chair)",
  "reason": "Verified original state board paper license copy."
}
```
- **Response**: `200 OK` with updated status preserving original agent recommendations in audit history.

---

### 5. Health Check
- **Method**: `GET`
- **Path**: `/health`
- **Response**: `200 OK` with status of Database, Local RAG, and LLM services.

---

### 6. System Info
- **Method**: `GET`
- **Path**: `/api/system/info`
- **Response**: `200 OK` with runtime configuration flags and disclaimers.
