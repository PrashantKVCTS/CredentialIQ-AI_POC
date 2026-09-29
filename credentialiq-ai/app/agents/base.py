"""Base agent class for CredentialIQ agentic framework."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Abstract base class for credentialing agents."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute agent task on state payload and return state updates."""
        pass
