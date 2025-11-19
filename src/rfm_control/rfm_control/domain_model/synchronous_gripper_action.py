from attr import dataclass
from rfm_control.domain_model.gripper_action import GripperAction


@dataclass(frozen=True)
class SynchronousGripperAction(GripperAction):
    gripper_aperture: float

