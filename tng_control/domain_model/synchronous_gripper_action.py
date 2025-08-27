from attr import dataclass
from tng_control.domain_model.gripper_action import GripperAction


@dataclass(frozen=True)
class SynchronousGripperAction(GripperAction):
    gripper_aperture: float
