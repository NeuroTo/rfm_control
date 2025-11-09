from abc import ABC, abstractmethod
from collections.abc import Sequence

from tng_control.rfm_control.domain_model.robot_action import RobotAction


class ModelOutputMapper(ABC):
    @abstractmethod
    def to_action(self, model_output) -> Sequence[RobotAction]:
        pass
