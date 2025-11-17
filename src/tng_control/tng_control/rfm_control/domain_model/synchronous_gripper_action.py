from attr import dataclass
from tng_control.rfm_control.domain_model.gripper_action import GripperAction


@dataclass(frozen=True)
class SynchronousGripperAction(GripperAction):
    gripper_aperture: float

