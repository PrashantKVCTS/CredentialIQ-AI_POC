import uuid
from typing import Optional, List, Dict
from app.core.models import CredentialingCase

class CredentialingCaseRepository:
    def __init__(self):
        self._cases: Dict[uuid.UUID, CredentialingCase] = {}

    async def save_case_async(self, case: CredentialingCase) -> CredentialingCase:
        self._cases[case.id] = case
        return case

    async def get_case_by_id_async(self, case_id: uuid.UUID) -> Optional[CredentialingCase]:
        return self._cases.get(case_id)

    async def get_case_by_correlation_id_async(self, correlation_id: str) -> Optional[CredentialingCase]:
        for case in self._cases.values():
            if case.correlation_id == correlation_id:
                return case
        return None

    async def list_cases_async(self) -> List[CredentialingCase]:
        return list(self._cases.values())
