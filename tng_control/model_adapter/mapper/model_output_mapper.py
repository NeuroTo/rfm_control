from abc import ABC, abstractmethod
from collections.abc import Sequence

from tng_control.action_adapter.actions.action import Action


class ModelOutputMapper(ABC):
    @abstractmethod
    def to_action(self, model_output) -> Sequence[Action]:
        pass
