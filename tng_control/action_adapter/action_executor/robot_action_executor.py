from abc import ABC, abstractmethod
from rclpy.task import Future
from rclpy.node import Node


class RobotActionExecutor(ABC):

    @abstractmethod
    def execute_action(self, action, node: Node) -> Future:
        pass
