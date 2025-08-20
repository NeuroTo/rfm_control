from abc import ABC
from attr import dataclass

from tng_control.action_adapter.actions.robot_action import RobotAction
from tng_control.action_adapter.actions.gripper_action import GripperAction


@dataclass(frozen=True)
class Action(ABC):
    robot_prefix: str
    timestep_id: int
    robot_action: RobotAction
    gripper_action: GripperAction
