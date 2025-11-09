from attr import dataclass
import numpy as np

from tng_control.rfm_control.domain_model.arm_action import ArmAction


@dataclass(frozen=True)
class AbsoluteJointStateAction(ArmAction):
    joint_states: np.ndarray  # one-dimensional array of floats
    joint_names: list[str] = []
    # TODO: set this value during runtime
    time_between_goals: float = 0.5  # seconds
