from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import rclpy
from rclpy.task import Future
from rclpy.node import Node


CommandType = TypeVar("CommandType")

class MotionExecutor(ABC, Generic[CommandType]):

    @abstractmethod
    def execute_async(self, command: CommandType, node: Node) -> Future: ...

    def execute_sync(self, command: CommandType, node: Node, timeout_sec: float = 5.0) -> bool: 
        """
        Execute the command synchronously and return True if the command was executed successfully, False otherwise.
        Be careful, this method will block the current thread until the command is executed or the timeout is reached.
        """
        future = self.execute_async(command, node)
        rclpy.spin_until_future_complete(node, future, timeout_sec=timeout_sec)
        if future.done() is not True:
            node.get_logger().warning(f"Action execution failed with result: {future.result()}")
            return False
        return True
