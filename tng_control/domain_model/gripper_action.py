from abc import ABC
from attr import dataclass


@dataclass(frozen=True)
class GripperAction(ABC):
    pass
