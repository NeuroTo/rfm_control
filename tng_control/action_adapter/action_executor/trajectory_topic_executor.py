from rclpy.task import Future
from rclpy.node import Node
from rclpy.publisher import Publisher
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from typing_extensions import override
from tng_control.action_adapter.action_executor.robot_action_executor import ArmActionExecutor
from rclpy.impl import rcutils_logger


class TrajectoryTopicExecutor(ArmActionExecutor):

    def __init__(self, topic_name: str, joint_names: list[str]):
        self.joint_names = joint_names
        self.topic_name = topic_name
        self.joint_trajectory_publisher: Publisher = None

        self.logger = rcutils_logger.RcutilsLogger(name="trajectory_topic_executor")

    @override
    def execute_action(self, action: list[JointTrajectoryPoint], node: Node) -> Future:
        if self.joint_trajectory_publisher is None:
            self.joint_trajectory_publisher = node.create_publisher(
                JointTrajectory, self.topic_name, 10)

        joint_trajectory: JointTrajectory = JointTrajectory(
            joint_names=self.joint_names,
            points=action
        )
        self.logger.info(f"sending action with following parameters:\n{self.joint_names}\n{action}")
        self.joint_trajectory_publisher.publish(joint_trajectory)

        overall_future = Future()
        overall_future.set_result(None)
        return overall_future
