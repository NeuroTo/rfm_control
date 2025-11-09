from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.task import Future
from control_msgs.action import GripperCommand as GripperCommandAction
from control_msgs.msg import GripperCommand as GripperCommandMessage


class GripperActionExecutor():

    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self._action_client = None

    def execute_gripper_action(
            self, action: GripperCommandMessage, node: Node) -> Future:
        overall_future = Future()
        goal: GripperCommandAction.Goal = GripperCommandAction.Goal()
        goal.command = action

        accepted_future: Future = self._get_action_client(node).send_goal_async(goal)
        accepted_future.add_done_callback(
            lambda x: GripperActionExecutor._done_callback(x, overall_future))
        return overall_future

    def _get_action_client(self, node: Node) -> ActionClient:
        if self._action_client is None:
            self._action_client = ActionClient(
                node, GripperCommandAction, self.topic_name
            )
        return self._action_client

    @staticmethod
    def _done_callback(result, overall_future: Future) -> None:
        if result.result() is None or not result.result().accepted:
            overall_future.set_exception(RuntimeError("gripper action rejected"))
            return
        future = result.result().get_result_async()
        future.add_done_callback(lambda x: GripperActionExecutor._result_done_cb(x, overall_future))

    @staticmethod
    def _result_done_cb(result_future, overall_future: Future) -> None:
        try:
            result = result_future.result().result
            overall_future.set_result(result=result)
        except Exception as e:
            overall_future.set_exception(e)
