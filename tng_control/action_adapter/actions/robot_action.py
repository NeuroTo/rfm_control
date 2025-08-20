from abc import ABC
from attr import dataclass


@dataclass(frozen=True)
class RobotAction(ABC):
    pass
