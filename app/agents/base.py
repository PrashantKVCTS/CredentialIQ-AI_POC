from abc import ABC, abstractmethod
from app.core.models import CredentialingCase

class ICredentialingAgent(ABC):
    @property
    @abstractmethod
    def agent_name(self) -> str:
        pass

    @abstractmethod
    async def process_async(self, case: CredentialingCase) -> CredentialingCase:
        pass
