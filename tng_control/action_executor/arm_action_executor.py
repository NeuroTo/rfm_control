from abc import ABC, abstractmethod
from rclpy.task import Future
from rclpy.node import Node

from tng_control.rfm_control.domain_model.arm_action import ArmAction


class ArmActionExecutor(ABC):

    # TODO: should not depend on rfm control
    @abstractmethod
    def execute_action(self, action: ArmAction, node: Node) -> Future:
        pass

