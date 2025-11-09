import sys
from typing import cast
from collections.abc import Sequence

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.model_adapter.adapter_provider import get_adapters, ConfigStrings
from tng_control.rfm_control.status_code import RfmControlStatusCode
from tng_control.rfm_control.exceptions import (
    ImageNotAvailableException, JointStatesNotAvailableException
)
from tng_control.rfm_control.domain_model.robot_action import RobotAction
from tng_robot_arms_custom_interfaces.action import MoveFromPrompt



NUM_ITERATIONS: int = 500  # number of iterations of calls to model and executing the action
ACTION_EXECUTION_HORIZON: int = 8  # number of actions to execute from an action chunk


class RfmActionServer(Node):

    def __init__(
            self, model_adapter: ModelPort, action_adapter: ActionPort) -> None:
        super().__init__('rfm_action_server')

        self._model_adapter: ModelPort = model_adapter
        self._action_port: ActionPort = action_adapter

        # Action server
        self._action_server: ActionServer = ActionServer(
            self,
            MoveFromPrompt,
            'rfm_action_server',
            self.move_from_prompt_callback
        )

        action_adapter.joint_state_subscriber.create_subscription(self)
        for observation_handler in model_adapter.observation_handler:
            observation_handler.create_subscription(self)

        self.get_logger().info('RFM Action Server has been started')

    def move_from_prompt_callback(
            self, goal_handle: MoveFromPrompt.Goal) -> MoveFromPrompt.Result:
        self.get_logger().info(
            f'Robot Control: Incoming request\na: {goal_handle.request.prompt}')

        for _ in range(NUM_ITERATIONS):
            error_type: RfmControlStatusCode = self._move_from_prompt(goal_handle.request.prompt)
            if error_type != RfmControlStatusCode.SUCCESS:
                goal_handle.abort()
                return MoveFromPrompt.Result(status_code=error_type.value)

        goal_handle.succeed()
        result: MoveFromPrompt.Result = MoveFromPrompt.Result(
            status_code=RfmControlStatusCode.SUCCESS.value)

        self.get_logger().info("Robot Control: Request completed successfully")
        return result

    def _move_from_prompt(self, prompt: str) -> RfmControlStatusCode:
        try:
            next_actions: Sequence[RobotAction] = self._model_adapter.get_action(prompt)
        except ImageNotAvailableException:
            return RfmControlStatusCode.IMAGES_UNAVAILABLE
        except JointStatesNotAvailableException:
            return RfmControlStatusCode.JOINTS_STATES_UNAVAILABLE

        return self._action_port.move(self, next_actions, ACTION_EXECUTION_HORIZON)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    conf_str: ConfigStrings = cast(ConfigStrings, sys.argv[1])

    model_port: ModelPort
    action_port: ActionPort
    model_port, action_port = get_adapters(conf_str)
    rfm_action_server = RfmActionServer(model_port, action_port)

    try:
        rclpy.spin(rfm_action_server)
    except KeyboardInterrupt:
        rclpy.shutdown()


if __name__ == "__main__":
    main()
