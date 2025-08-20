from attr import dataclass
import numpy as np

from tng_control.action_adapter.actions.robot_action import RobotAction


@dataclass(frozen=True)
class DeltaEndeffectorAction(RobotAction):
    position: np.ndarray  # position deltas
    orientation: np.ndarray  # rpy deltas
