from rclpy.task import Future
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory
from typing_extensions import override
from tng_control.action_executor.arm_action_executor import ArmActionExecutor


class TrajectoryActionExecutor(ArmActionExecutor):

    def __init__(self, topic_name: str, joint_names: list[str]):
        self.joint_names = joint_names
        self.topic_name = topic_name
        self._action_client = None

    @override
    def execute_action(self, node: Node, action: JointTrajectory) -> Future:
        overall_future = Future()
        joint_trajectory: JointTrajectory = action

        goal: FollowJointTrajectory.Goal = FollowJointTrajectory.Goal(trajectory=joint_trajectory)

        accepted_future: Future = self._get_action_client(node).send_goal_async(
            goal)

        accepted_future.add_done_callback(
            lambda x: TrajectoryActionExecutor._done_callback(x, overall_future))
        return overall_future

    def _get_action_client(self, node: Node) -> ActionClient:
        if self._action_client is None:
            self._action_client = ActionClient(
                node, FollowJointTrajectory, self.topic_name
            )
        return self._action_client

    @staticmethod
    def _done_callback(result, overall_future: Future):
        if result.result() is None or not result.result().accepted:
            raise RuntimeError("follow joint trajectory goal handle rejected")
        future = result.result().get_result_async()
        future.add_done_callback(
            lambda x: TrajectoryActionExecutor._result_done_cb(x, overall_future)
        )

    @staticmethod
    def _result_done_cb(result_future, overall_future: Future):
        try:
            result = result_future.result().result
            overall_future.set_result(result=result)
        except Exception as e:
            overall_future.set_exception(e)
