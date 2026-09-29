import uuid
from typing import List
from app.agents.base import ICredentialingAgent
from app.core.models import CredentialingCase
from app.infrastructure.repository import CredentialingCaseRepository

class CredentialingOrchestrator:
    def __init__(self, agents: List[ICredentialingAgent], repository: CredentialingCaseRepository):
        self.agents = agents
        self.repository = repository

    async def run_pipeline_async(self, case: CredentialingCase) -> CredentialingCase:
        for agent in self.agents:
            case = await agent.process_async(case)

        await self.repository.save_case_async(case)
        return case
