from attr import dataclass
import numpy as np

from tng_control.rfm_control.domain_model.arm_action import ArmAction


@dataclass(frozen=True)
class DeltaEndeffectorAction(ArmAction):
    position: np.ndarray  # position deltas
    orientation: np.ndarray  # rpy deltas
    # TODO: set this value during runtime
    time_between_goals: float = 0.5  # seconds

