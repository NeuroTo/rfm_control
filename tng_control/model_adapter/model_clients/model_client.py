from abc import ABC, abstractmethod
from typing import Any


class ModelClient(ABC):
    """Common Interface for all polices.
    The policy client is responsible for the communication with the inference backend.
    It receives an observation and a prompt and returns an action.
    The format of the observatio and the action depends on the model.
    """

    @abstractmethod
    def get_action(self, observation: dict[str, Any], prompt: str) -> dict[str, Any]:
        pass
