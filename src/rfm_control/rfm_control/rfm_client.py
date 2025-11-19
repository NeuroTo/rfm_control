import sys

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.task import Future
from action_msgs.msg import GoalStatus

from rfm_control.status_code import RfmControlStatusCode
from custom_rfm_interfaces.action import MoveFromPrompt


class RfmClient(Node):

    def __init__(self) -> None:
        super().__init__('rfm_client')
        self.__action_client: ActionClient = ActionClient(
            self, MoveFromPrompt, "rfm_action_server")

    def send_goal(self, prompt: str) -> None:
        goal_msg: MoveFromPrompt.Goal = MoveFromPrompt.Goal()
        goal_msg.prompt = prompt

        self.__action_client.wait_for_server()

        send_goal_future: Future = self.__action_client.send_goal_async(
            goal_msg)

        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future: Future) -> None:
        goal_handle: ClientGoalHandle | None = future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        get_result_future: Future = goal_handle.get_result_async()

        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future: Future) -> None:
        result: MoveFromPrompt.Result | None = future.result()

        if result is None:
            self.get_logger().warn("rfm action failed")
        elif result.status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().warn(
                f"rfm action failed: {RfmControlStatusCode(result.result.status_code).name}")
        else:
            self.get_logger().info(
                f'Result:\n{result.result.gripper_positions}\n{result.result.gripper_poses}')
        rclpy.shutdown()


def main() -> None:
    rclpy.init()

    rfm_client: RfmClient = RfmClient()
    rfm_client.send_goal(str(sys.argv[1]))
    rclpy.spin(rfm_client)


if __name__ == '__main__':
    main()
