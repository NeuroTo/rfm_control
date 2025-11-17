from rclpy.task import Future
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory
from typing_extensions import override
from tng_control.action_executor.motion_executor import MotionExecutor


class JointTrajectoryActionExecutor(MotionExecutor[JointTrajectory]):

    def __init__(self, topic_name: str):
        self._topic_name = topic_name
        self._action_client = None

    @override
    def execute_async(self, command: JointTrajectory, node: Node) -> Future:
        overall_future = Future()

        goal: FollowJointTrajectory.Goal = FollowJointTrajectory.Goal(trajectory=command)

        accepted_future: Future = self._get_action_client(node).send_goal_async(
            goal)

        accepted_future.add_done_callback(
            lambda x: JointTrajectoryActionExecutor._done_callback(x, overall_future))
        return overall_future

    def _get_action_client(self, node: Node) -> ActionClient:
        # TODO: why not initialize the action client in the constructor?
        if self._action_client is None:
            self._action_client = ActionClient(
                node, FollowJointTrajectory, self._topic_name
            )
        return self._action_client

    @staticmethod
    def _done_callback(result, overall_future: Future):
        if result.result() is None or not result.result().accepted:
            raise RuntimeError("follow joint trajectory goal handle rejected")
        future = result.result().get_result_async()
        future.add_done_callback(
            lambda x: JointTrajectoryActionExecutor._result_done_cb(x, overall_future)
        )

    @staticmethod
    def _result_done_cb(result_future, overall_future: Future):
        try:
            result = result_future.result().result
            overall_future.set_result(result=result)
        except Exception as e:
            overall_future.set_exception(e)
