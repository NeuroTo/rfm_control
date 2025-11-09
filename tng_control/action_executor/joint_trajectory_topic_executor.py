from rclpy.task import Future
from rclpy.node import Node
from rclpy.publisher import Publisher
from trajectory_msgs.msg import JointTrajectory
from typing_extensions import override
from tng_control.action_executor.arm_action_executor import MotionExecutor
from rclpy.impl import rcutils_logger


class JointTrajectoryTopicExecutor(MotionExecutor[JointTrajectory]):

    def __init__(self, topic_name: str):
        self._topic_name = topic_name
        self._joint_trajectory_publisher: Publisher | None = None

        self._logger = rcutils_logger.RcutilsLogger(name="joint_trajectory_topic_executor")

    @override
    def execute_async(self, command: JointTrajectory, node: Node) -> Future:
        if self._joint_trajectory_publisher is None:
            self._joint_trajectory_publisher = node.create_publisher(
                JointTrajectory, self._topic_name, 10)
        self._logger.info(f"sending action with following parameters:\n{command.joint_names}\n{command.points}")
        self._joint_trajectory_publisher.publish(command)

        overall_future = Future()
        overall_future.set_result(None)
        return overall_future
