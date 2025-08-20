from attr import dataclass
import numpy as np

from tng_control.action_adapter.actions.robot_action import RobotAction


@dataclass(frozen=True)
class AbsoluteJointStateAction(RobotAction):
    joint_states: np.ndarray  # one-dimensional array of floats
    joint_names: list[str] = []
