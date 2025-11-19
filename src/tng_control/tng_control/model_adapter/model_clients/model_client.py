from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


ModelActionType = TypeVar("ModelActionType")


class ModelClient(ABC, Generic[ModelActionType]):
    """Common Interface for all polices.
    The policy client is responsible for the communication with the inference backend.
    It receives an observation and a prompt and returns an action.
    The format of the returned action depends on the model and is defined by the ModelActionType parameter.
    """

    @abstractmethod
    def get_action(self, observation: dict[str, Any], prompt: str) -> ModelActionType:
        pass
