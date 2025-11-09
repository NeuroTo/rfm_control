from abc import ABC, abstractmethod
import numpy as np
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

from tng_control.rfm_control.domain_model.arm_action import ArmAction


class ActionMapper(ABC):

    @abstractmethod
    def action_to_joint_trajectory_point(
            self, action: ArmAction, state: JointState) -> JointTrajectoryPoint | None:
        pass
