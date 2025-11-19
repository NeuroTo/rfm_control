from abc import ABC
from attr import dataclass


@dataclass(frozen=True)
class ArmAction(ABC):
    # TODO: is this the right place for the time_between_goals?
    time_between_goals: float # seconds
