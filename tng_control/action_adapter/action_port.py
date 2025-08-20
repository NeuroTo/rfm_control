from abc import ABC, abstractmethod
from collections.abc import Sequence
from rclpy.node import Node
from tng_control.action_adapter.actions.action import Action
from tng_control.rfm_control_status_code import RfmControlStatusCode
from tng_control.action_adapter.robot import Robot
from tng_control.model_adapter.observation_handler.joint_state_handler import JointStateHandler


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
    def move(self, actions: Sequence[Action], node: Node) -> RfmControlStatusCode:
        pass
