import sys
from collections.abc import Sequence

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from rfm_control.model_adapter.model_port import ModelPort
from rfm_control.action_adapter.action_port import ActionPort
from rfm_control.adapter_provider import AdapterProvider
from rfm_control.status_code import RfmControlStatusCode
from rfm_control.exceptions import (
    ImageNotAvailableException, JointStatesNotAvailableException
)
from rfm_control.domain_model.robot_action import RobotAction
from custom_rfm_interfaces.action import MoveFromPrompt



NUM_ITERATIONS: int = 500  # number of iterations of calls to model and executing the action
ACTION_EXECUTION_HORIZON: int = 8  # number of actions to execute from an action chunk


class RfmActionServer(Node):

    def __init__(
            self, model_adapter: ModelPort, action_adapter: ActionPort) -> None:
        super().__init__('rfm_action_server')

        self._model_port: ModelPort = model_adapter
        self._action_port: ActionPort = action_adapter

        # Action server
        self._action_server: ActionServer = ActionServer(
            self,
            MoveFromPrompt,
            'rfm_action_server',
            self.move_from_prompt_callback
        )

        action_adapter.joint_state_handler.create_subscription(self)
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
            next_actions: Sequence[RobotAction] = self._model_port.get_action(prompt)
        except ImageNotAvailableException:
            return RfmControlStatusCode.IMAGES_UNAVAILABLE
        except JointStatesNotAvailableException:
            return RfmControlStatusCode.JOINTS_STATES_UNAVAILABLE

        return self._action_port.move(self, next_actions, ACTION_EXECUTION_HORIZON)


def main(args: list[str] | None = None) -> None:
    """
    Start RFM Action Server with YAML configuration.
    
    Usage:
        ros2 run rfm_control rfm_action_server config/configs/gr00t_so101.yaml
    
    Args:
        args: Command line arguments (expects YAML config path as first arg)
    """
    rclpy.init(args=args)
    
    if len(sys.argv) < 2:
        raise ValueError(
            "Missing configuration file argument.\n"
            "Usage: ros2 run rfm_control rfm_action_server <config_file.yaml>\n"
            "Example: ros2 run rfm_control rfm_action_server config/configs/gr00t_so101.yaml"
        )
    
    config_path: str = sys.argv[1]

    provider = AdapterProvider()
    model_port: ModelPort
    action_port: ActionPort
    model_port, action_port = provider.get_adapters(config_path)
    rfm_action_server = RfmActionServer(model_port, action_port)

    try:
        rclpy.spin(rfm_action_server)
    except KeyboardInterrupt:
        rclpy.shutdown()


if __name__ == "__main__":
    main()
