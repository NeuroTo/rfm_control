from abc import ABC, abstractmethod
from collections.abc import Sequence
from rclpy.node import Node
from rfm_control.domain_model.robot_action import RobotAction
from rfm_control.status_code import RfmControlStatusCode
from rfm_control.action_adapter.robot import Robot
from rfm_control.observation_handler.joint_state_handler import JointStateHandler


class ActionPort(ABC):

    @property
    @abstractmethod
    def robots(self) -> Sequence[Robot]:
        pass

    @property
    @abstractmethod
    def joint_state_handler(self) -> JointStateHandler:
        pass

    @abstractmethod
    def move(self, node: Node, actions: Sequence[RobotAction], action_execution_horizon: int) -> RfmControlStatusCode:
        pass
