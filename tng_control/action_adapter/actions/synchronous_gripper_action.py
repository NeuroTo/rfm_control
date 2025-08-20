from attr import dataclass
from tng_control.action_adapter.actions.gripper_action import GripperAction


@dataclass(frozen=True)
class SynchronousGripperAction(GripperAction):
    gripper_aperture: float
