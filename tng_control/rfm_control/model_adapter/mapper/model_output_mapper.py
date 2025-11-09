from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from tng_control.rfm_control.domain_model.robot_action import RobotAction


ModelOutputType = TypeVar("ModelOutputType")


class ModelOutputMapper(ABC, Generic[ModelOutputType]):
    """
    Maps model-specific output to a sequence of RobotActions.
    ModelOutputType represents the format of the model's output (e.g., Gr00tAction or OctoAction).
    """
    
    @abstractmethod
    def to_action(self, model_output: ModelOutputType) -> Sequence[RobotAction]:
        pass
