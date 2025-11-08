from abc import ABC, abstractmethod
from collections.abc import Sequence
from rclpy.node import Node
from tng_control.domain_model.robot_action import RobotAction
from tng_control.rfm_control.status_code import RfmControlStatusCode
from tng_control.action_adapter.robot import Robot
from tng_control.action_adapter.joint_state_subscriber import JointStateSubscriber


class ActionPort(ABC):

    @property
    @abstractmethod
    def robots(self) -> Sequence[Robot]:
        pass

    @property
    @abstractmethod
    def joint_state_subscriber(self) -> JointStateSubscriber:
        pass

    @abstractmethod
    def move(self, actions: Sequence[RobotAction], node: Node) -> RfmControlStatusCode:
        pass
