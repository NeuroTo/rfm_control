from abc import ABC, abstractmethod
import numpy as np
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

from tng_control.action_adapter.actions.robot_action import RobotAction


class ActionMapper(ABC):

    @abstractmethod
    def action_to_joint_trajectory_point(
            self, action: RobotAction, state: JointState) -> JointTrajectoryPoint | None:
        pass

    @abstractmethod
    def action_to_delta(self, action: RobotAction, state: JointState) -> np.ndarray | None:
        pass
