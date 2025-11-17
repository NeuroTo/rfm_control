from abc import ABC
from attr import dataclass

from tng_control.rfm_control.domain_model.arm_action import ArmAction
from tng_control.rfm_control.domain_model.gripper_action import GripperAction


@dataclass(frozen=True)
class RobotAction(ABC):
    robot_prefix: str
    timestep_id: int
    arm_action: ArmAction
    gripper_action: GripperAction

